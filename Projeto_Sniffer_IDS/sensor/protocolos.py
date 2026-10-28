"""Etapas 2 e 3: decodificar Modbus TCP e S7comm à mão.

Cada decodificador recebe um Segmento (bytes do TCP) e devolve um Evento: o mesmo
formato para qualquer protocolo. Daqui para frente, ninguém mais precisa saber o que
é Modbus ou S7.

Todos os números dos dois protocolos são big-endian: no struct, o formato começa com ">".

Em C (ESP32): event_t, proto_modbus.c, proto_s7.c. O dicionário DECODIFICADORES vira um
vetor de struct proto_t com ponteiros de função, e PENDENTES vira uma tabela fixa.
"""

import struct
import time
from dataclasses import dataclass, field


@dataclass
class Evento:
    ts: float
    origem: str
    destino: str
    protocolo: str              # "modbus", "s7", "s7plus"
    direcao: str                # "pergunta" ou "resposta"
    operacao: str               # "leitura", "escrita", "controle", "diagnostico", "outra"
    funcao: int
    area: str = ""
    endereco: int = 0
    quantidade: int = 0
    status: int = 0             # 0 = ok; senão, código de erro do protocolo
    valores: list = field(default_factory=list)

    def __str__(self):
        hora = time.strftime("%H:%M:%S", time.localtime(self.ts))
        funcao = f"0x{self.funcao:02X}" if self.protocolo.startswith("s7") else str(self.funcao)
        texto = (f"{hora} {self.origem:>15} -> {self.destino:<15} {self.protocolo:6} "
                 f"{self.direcao:8} {self.operacao:11} f={funcao:<4}")
        if self.area:
            texto += f" {self.area} end={self.endereco} qtd={self.quantidade}"
        if self.valores:
            texto += f" valores={self.valores}"
        if self.status:
            texto += f" ERRO=0x{self.status:04X}"
        return texto


# Perguntas esperando resposta. A resposta não repete o endereço pedido, então guardamos
# a pergunta pela chave (cliente, servidor, protocolo, identificador).
PENDENTES = {}
LIMITE_PENDENTES = 1000


def guardar_pergunta(chave, ev):
    if len(PENDENTES) >= LIMITE_PENDENTES:
        PENDENTES.pop(next(iter(PENDENTES)))         # tira a mais antiga
    PENDENTES[chave] = (ev.funcao, ev.area, ev.endereco, ev.quantidade)


def completar_resposta(chave, ev):
    """Copia função, área, endereço e quantidade da pergunta para a resposta."""
    pergunta = PENDENTES.pop(chave, None)
    if pergunta:
        funcao, ev.area, ev.endereco, ev.quantidade = pergunta
        if not ev.funcao:
            ev.funcao = funcao


def palavras(dados):
    """Primeiros registradores de 16 bits de um bloco de bytes (no máximo 4)."""
    n = min(len(dados) // 2, 4)
    return list(struct.unpack(f">{n}H", dados[:n * 2]))


# ---------------------------------------------------------------- Modbus TCP (porta 502)

MODBUS_OPERACAO = {1: "leitura", 2: "leitura", 3: "leitura", 4: "leitura",
                   5: "escrita", 6: "escrita", 15: "escrita", 16: "escrita",
                   8: "diagnostico", 43: "diagnostico"}
MODBUS_AREA = {1: "coil", 2: "entrada", 3: "holding", 4: "input",
               5: "coil", 6: "holding", 15: "coil", 16: "holding"}


def decodificar_modbus(seg):
    d = seg.payload
    if len(d) < 8:
        return None

    # Cabeçalho MBAP (7 bytes) + código de função (1 byte)
    transacao, protocolo, tamanho, unidade, funcao = struct.unpack(">HHHBB", d[:8])
    if protocolo != 0 or len(d) != 6 + tamanho:
        return None                     # não é Modbus, ou não é UMA mensagem inteira

    pergunta = seg.porta_destino == 502
    excecao = funcao & 0x80             # bit 7 ligado = resposta de erro
    funcao = funcao & 0x7F
    corpo = d[8:]

    ev = Evento(seg.ts, seg.ip_origem, seg.ip_destino, "modbus",
                "pergunta" if pergunta else "resposta",
                MODBUS_OPERACAO.get(funcao, "outra"), funcao, MODBUS_AREA.get(funcao, ""))

    cliente, servidor = (seg.ip_origem, seg.ip_destino) if pergunta else (seg.ip_destino, seg.ip_origem)
    chave = (cliente, servidor, "modbus", transacao)

    if pergunta:
        if len(corpo) >= 4:
            ev.endereco, ev.quantidade = struct.unpack(">HH", corpo[:4])
        if funcao in (5, 6):            # escrita simples: o segundo campo é o valor
            ev.valores, ev.quantidade = [ev.quantidade], 1
        if funcao == 16 and len(corpo) >= 5:
            ev.valores = palavras(corpo[5:5 + corpo[4]])
        guardar_pergunta(chave, ev)
    else:
        completar_resposta(chave, ev)
        if excecao:
            ev.status = corpo[0] if corpo else 0xFF
        elif funcao in (3, 4) and corpo:
            ev.valores = palavras(corpo[1:1 + corpo[0]])
    return ev


# ---------------------------------------------------------------- S7comm (porta 102)

S7_OPERACAO = {0xF0: "outra", 0x04: "leitura", 0x05: "escrita", 0x28: "controle", 0x29: "controle",
               0x1A: "controle", 0x1B: "controle", 0x1C: "controle",      # download de programa
               0x1D: "controle", 0x1E: "controle", 0x1F: "controle"}      # upload de programa
S7_AREA = {0x81: "entradas", 0x82: "saidas", 0x83: "memorias", 0x84: "DB"}


def decodificar_s7(seg):
    d = seg.payload

    # TPKT (4 bytes): versão 3, reservado, tamanho total
    if len(d) < 7 or d[0] != 0x03:
        return None
    if struct.unpack(">H", d[2:4])[0] != len(d):
        return None                     # não é UMA mensagem inteira

    # COTP: d[4] = tamanho do resto do cabeçalho COTP; d[5] = tipo. 0xF0 = dados.
    if d[5] != 0xF0:
        return None                     # pedido/confirmação de conexão: ainda não é S7
    s7 = d[5 + d[4]:]

    pergunta = seg.porta_destino == 102
    cliente, servidor = (seg.ip_origem, seg.ip_destino) if pergunta else (seg.ip_destino, seg.ip_origem)

    if len(s7) >= 1 and s7[0] == 0x72:  # S7comm-plus: TIA Portal, protegido. Só registramos.
        return Evento(seg.ts, seg.ip_origem, seg.ip_destino, "s7plus",
                      "pergunta" if pergunta else "resposta", "outra", 0)
    if len(s7) < 10 or s7[0] != 0x32:
        return None

    # Cabeçalho S7: 0x32, ROSCTR, reservado(2), PDU ref(2), tam. parâmetros(2), tam. dados(2)
    rosctr = s7[1]                      # 1 = pedido, 2/3 = resposta, 7 = userdata
    pdu_ref, tam_param, tam_dados = struct.unpack(">HHH", s7[4:10])
    cabecalho = 12 if rosctr in (2, 3) else 10       # respostas trazem classe e código de erro
    if len(s7) < cabecalho + tam_param + tam_dados:
        return None
    param = s7[cabecalho:cabecalho + tam_param]
    dados = s7[cabecalho + tam_param:cabecalho + tam_param + tam_dados]

    if rosctr == 7:                     # userdata: diagnóstico, lista de blocos, relógio...
        return Evento(seg.ts, seg.ip_origem, seg.ip_destino, "s7",
                      "pergunta" if pergunta else "resposta", "diagnostico", 0)

    funcao = param[0] if param else 0
    ev = Evento(seg.ts, seg.ip_origem, seg.ip_destino, "s7",
                "pergunta" if pergunta else "resposta", S7_OPERACAO.get(funcao, "outra"), funcao)
    chave = (cliente, servidor, "s7", pdu_ref)

    if pergunta:
        # Read/Write Var: param = função, nº de itens, e itens de 12 bytes. Lemos só o 1º item.
        if funcao in (0x04, 0x05) and len(param) >= 14 and param[2] == 0x12:
            item = param[2:14]
            ev.quantidade, db = struct.unpack(">HH", item[4:8])
            ev.area = f"DB{db}" if item[8] == 0x84 else S7_AREA.get(item[8], hex(item[8]))
            ev.endereco = int.from_bytes(item[9:12], "big") >> 3      # vem em bits
        if funcao == 0x05 and len(dados) >= 4:
            ev.valores = palavras(dados[4:])
        guardar_pergunta(chave, ev)
    else:
        completar_resposta(chave, ev)
        ev.operacao = S7_OPERACAO.get(ev.funcao, "outra")
        erro = struct.unpack(">H", s7[10:12])[0]       # ex.: 0x8104 = PUT/GET não permitido
        if erro:
            ev.status = erro
        elif dados and dados[0] != 0xFF:               # código de retorno do item
            ev.status = dados[0]                       # 0x05 endereço inválido, 0x0A não existe
        elif ev.funcao == 0x04 and len(dados) >= 4:
            ev.valores = palavras(dados[4:])
    return ev


# ---------------------------------------------------------------- escolha pelo número da porta

DECODIFICADORES = {502: decodificar_modbus, 102: decodificar_s7}


def decodificar(seg):
    """Escolhe o decodificador pela porta do servidor e devolve um Evento (ou None)."""
    porta = seg.porta_destino if seg.porta_destino in DECODIFICADORES else seg.porta_origem
    decodificador = DECODIFICADORES.get(porta)
    return decodificador(seg) if decodificador else None
