"""CLP simulado: servidor Modbus TCP com o mesmo contrato do S7-1200 (ADR-002).

Serve para desenvolver e testar sem bancada e como contingência na aula.
Implementa FC 3, FC 6 e FC 16, aceita uma conexão por vez (como uma instância
de MB_SERVER) e simula a planta com a mesma lógica do programa Planta.scl.

Uso:
    python clp_simulado.py                 # escuta em 127.0.0.1:5020
    python clp_simulado.py --host 0.0.0.0 --porta 502

Teclas (digite a letra e Enter) para simular a bancada:
    l  chave em LOCAL          r  chave em REMOTO
    e  aperta/solta emergência f  falha do inversor liga/desliga
    q  aquecimento extra (testa o alarme de 80 °C) liga/desliga
"""

import argparse
import asyncio
import logging
import random
import struct
import threading
import time

import contrato as c

VEL_MAX = 1700            # rpm (ADR-003, premissa)
LIMITE_TEMPERATURA = 80.0  # °C (ADR-003, premissa)
WATCHDOG_S = 3.0          # ADR-005
RAMPA_RPM_S = 500.0
PASSO_S = 0.1

log = logging.getLogger("clp_simulado")


class Planta:
    """Estado da planta e lógica do CLP, executados a cada PASSO_S."""

    def __init__(self):
        self.hr = [0] * c.TOTAL_REGISTRADORES
        self.trava = threading.Lock()
        self.temperatura = 25.0
        self.velocidade = 0.0
        self.motor_ligado = False
        self.modo_remoto = True
        self.emergencia = False
        self.falha_inversor = False
        self.aquecimento_extra = False
        self.codigo_falha = 0
        self.ultimo_heartbeat = None
        self.instante_heartbeat = time.monotonic()
        self.ultimo_cmd_motor = None

    def passo(self, dt):
        with self.trava:
            hr = self.hr
            agora = time.monotonic()

            # watchdog do heartbeat (HR12)
            if hr[c.HR_HEARTBEAT] != self.ultimo_heartbeat:
                self.ultimo_heartbeat = hr[c.HR_HEARTBEAT]
                self.instante_heartbeat = agora
            heartbeat_ausente = agora - self.instante_heartbeat > WATCHDOG_S

            # causas de falha
            if self.emergencia:
                self.codigo_falha = 3
            elif self.falha_inversor:
                self.codigo_falha = 1
            elif self.temperatura > LIMITE_TEMPERATURA:
                self.codigo_falha = 4
            elif heartbeat_ausente and self.motor_ligado:
                self.codigo_falha = 2

            # comando do motor (HR11): 0 parar, 1 ligar, 2 reconhecer
            cmd = hr[c.HR_CMD_MOTOR]
            if cmd == c.CMD_RECONHECER:
                causa_ativa = (self.emergencia or self.falha_inversor
                               or self.temperatura > LIMITE_TEMPERATURA)
                if not causa_ativa:
                    self.codigo_falha = 0
                hr[c.HR_CMD_MOTOR] = c.CMD_PARAR

            pode_ligar = (self.modo_remoto and self.codigo_falha == 0
                          and not heartbeat_ausente)
            self.motor_ligado = hr[c.HR_CMD_MOTOR] == c.CMD_LIGAR and pode_ligar

            # parada por falha, modo local ou heartbeat: o CLP zera o comando,
            # para que o motor nunca religue sozinho quando a causa sumir
            if not pode_ligar:
                hr[c.HR_CMD_MOTOR] = c.CMD_PARAR

            # referência limitada a VEL_MAX
            pedida = hr[c.HR_CMD_VELOCIDADE]
            aplicada = min(pedida, VEL_MAX)
            alvo = aplicada if self.motor_ligado else 0
            passo_max = RAMPA_RPM_S * dt
            self.velocidade += max(-passo_max, min(passo_max, alvo - self.velocidade))

            # temperatura sobe com a velocidade (constante de tempo de 60 s)
            final = 25.0 + 30.0 * self.velocidade / VEL_MAX + (70.0 if self.aquecimento_extra else 0)
            self.temperatura += (final - self.temperatura) * dt / 60.0
            medida = self.temperatura + random.uniform(-0.1, 0.1)

            # área de leitura
            hr[c.HR_TEMPERATURA] = c.para_word(round(medida * c.ESCALA_TEMPERATURA))
            hr[c.HR_VELOCIDADE] = round(self.velocidade)
            hr[c.HR_REFERENCIA] = aplicada
            hr[c.HR_FALHA] = self.codigo_falha
            hr[c.HR_STATUS] = c.codificar_status({
                "motor_ligado": self.motor_ligado,
                "modo_remoto": self.modo_remoto,
                "falha_inversor": self.falha_inversor,
                "heartbeat_perdido": heartbeat_ausente,
                "referencia_limitada": pedida > VEL_MAX,
                "emergencia": self.emergencia,
            })

    def ler(self, inicio, quantidade):
        with self.trava:
            return self.hr[inicio:inicio + quantidade]

    def escrever(self, inicio, valores):
        with self.trava:
            self.hr[inicio:inicio + len(valores)] = valores


# ---------------------------------------------------------------- servidor Modbus TCP

def excecao(funcao, codigo):
    return struct.pack(">BB", funcao | 0x80, codigo)


def processar_pdu(planta, pdu):
    """Recebe a PDU (código de função + dados) e devolve a PDU de resposta."""
    funcao = pdu[0]
    try:
        if funcao == 3:
            inicio, qtd = struct.unpack(">HH", pdu[1:5])
            if not 1 <= qtd <= 125:
                return excecao(funcao, 3)
            if inicio + qtd > c.TOTAL_REGISTRADORES:
                return excecao(funcao, 2)
            valores = planta.ler(inicio, qtd)
            return struct.pack(f">BB{qtd}H", 3, 2 * qtd, *valores)
        if funcao == 6:
            endereco, valor = struct.unpack(">HH", pdu[1:5])
            if endereco >= c.TOTAL_REGISTRADORES:
                return excecao(funcao, 2)
            planta.escrever(endereco, [valor])
            return pdu[:5]
        if funcao == 16:
            inicio, qtd, nbytes = struct.unpack(">HHB", pdu[1:6])
            if not 1 <= qtd <= 123 or nbytes != 2 * qtd:
                return excecao(funcao, 3)
            if inicio + qtd > c.TOTAL_REGISTRADORES:
                return excecao(funcao, 2)
            valores = list(struct.unpack(f">{qtd}H", pdu[6:6 + nbytes]))
            planta.escrever(inicio, valores)
            return struct.pack(">BHH", 16, inicio, qtd)
        return excecao(funcao, 1)
    except struct.error:
        return excecao(funcao, 3)


class Servidor:
    def __init__(self, planta):
        self.planta = planta
        self.ocupado = False

    async def atender(self, leitor, escritor):
        par = escritor.get_extra_info("peername")
        if self.ocupado:
            # MB_SERVER com uma instância: só uma conexão por vez (ADR-004)
            log.warning("conexão de %s recusada: já existe um cliente", par)
            escritor.close()
            return
        self.ocupado = True
        log.info("cliente conectado: %s", par)
        try:
            while True:
                mbap = await leitor.readexactly(7)
                transacao, protocolo, tamanho, unidade = struct.unpack(">HHHB", mbap)
                pdu = await leitor.readexactly(tamanho - 1)
                resposta = processar_pdu(self.planta, pdu)
                escritor.write(struct.pack(">HHHB", transacao, 0, len(resposta) + 1, unidade) + resposta)
                await escritor.drain()
        except (asyncio.IncompleteReadError, ConnectionError):
            pass
        finally:
            self.ocupado = False
            escritor.close()
            log.info("cliente desconectado: %s", par)


async def simular(planta):
    while True:
        planta.passo(PASSO_S)
        await asyncio.sleep(PASSO_S)


async def principal(host, porta, planta):
    servidor = Servidor(planta)
    srv = await asyncio.start_server(servidor.atender, host, porta)
    log.info("CLP simulado escutando em %s:%s", host, porta)
    async with srv:
        await asyncio.gather(srv.serve_forever(), simular(planta))


def teclado(planta):
    acoes = {
        "l": ("modo_remoto", False), "r": ("modo_remoto", True),
    }
    alternar = {"e": "emergencia", "f": "falha_inversor", "q": "aquecimento_extra"}
    while True:
        try:
            tecla = input().strip().lower()
        except EOFError:
            return
        with planta.trava:
            if tecla in acoes:
                atributo, valor = acoes[tecla]
                setattr(planta, atributo, valor)
            elif tecla in alternar:
                atributo = alternar[tecla]
                setattr(planta, atributo, not getattr(planta, atributo))
            else:
                continue
        log.info("remoto=%s emergencia=%s falha_inversor=%s aquecimento=%s",
                 planta.modo_remoto, planta.emergencia, planta.falha_inversor,
                 planta.aquecimento_extra)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--porta", type=int, default=5020)
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [clp_simulado] %(message)s")
    planta = Planta()
    threading.Thread(target=teclado, args=(planta,), daemon=True).start()
    try:
        asyncio.run(principal(args.host, args.porta, planta))
    except KeyboardInterrupt:
        pass
