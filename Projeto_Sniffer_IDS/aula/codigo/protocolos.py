import struct
from dataclasses import dataclass, field


@dataclass
class Evento:
    ts: float
    origem: str
    destino: str
    protocolo: str     # "modbus" ou "s7"
    direcao: str       # "pergunta" ou "resposta"
    operacao: str      # "leitura", "escrita", "controle", "outra"
    funcao: int        # código da função no protocolo
    area: str = ""
    endereco: int = 0
    quantidade: int = 0
    status: int = 0    # 0 = ok; senão, código de erro
    valores: list = field(default_factory=list)
    def __str__(self):
        return (f"{self.origem:>15} -> {self.destino:<15} "
                f"{self.protocolo:6} {self.direcao:8} {self.operacao:9}"
                f" f={self.funcao:#04x} {self.area} end={self.endereco}"
                f" qtd={self.quantidade} {self.valores}"
                f" status={self.status:#06x}")


PENDENTES = {}        # perguntas esperando resposta
DECODIFICADORES = {}  # porta do servidor -> função que decodifica


def palavras(dados):
    """Até 4 números de 16 bits (big-endian) do início de dados."""
    n = min(len(dados) // 2, 4)
    return list(struct.unpack(f">{n}H", dados[:n * 2]))


def decodificar(seg):
    porta = (seg.porta_destino if seg.porta_destino in DECODIFICADORES
             else seg.porta_origem)
    funcao = DECODIFICADORES.get(porta)
    return funcao(seg) if funcao else None


MODBUS_OPERACAO = {1: "leitura", 2: "leitura", 3: "leitura",
                   4: "leitura", 5: "escrita", 6: "escrita",
                   15: "escrita", 16: "escrita"}


def decodificar_modbus(seg):
    d = seg.payload
    if len(d) < 8:
        return None
    # MBAP (7 bytes) + função (1 byte), tudo big-endian (">")
    transacao, protocolo, tamanho, unidade, funcao = struct.unpack(
        ">HHHBB", d[:8])
    if protocolo != 0 or len(d) != 6 + tamanho:
        return None              # não é UMA mensagem Modbus inteira
    pergunta = seg.porta_destino == 502
    erro = funcao & 0x80         # bit 7 ligado = resposta de erro
    funcao = funcao & 0x7F
    corpo = d[8:]
    ev = Evento(seg.ts, seg.ip_origem, seg.ip_destino, "modbus",
                "pergunta" if pergunta else "resposta",
                MODBUS_OPERACAO.get(funcao, "outra"), funcao)
    if pergunta:
        if len(corpo) >= 4:
            ev.endereco, ev.quantidade = struct.unpack(">HH", corpo[:4])
        if funcao in (5, 6):     # escrita simples: o 2o campo é o valor
            ev.valores, ev.quantidade = [ev.quantidade], 1
        PENDENTES[("modbus", seg.ip_origem, transacao)] = ev
    else:
        p = PENDENTES.pop(("modbus", seg.ip_destino, transacao), None)
        if p:                    # a resposta não repete o endereço
            ev.endereco, ev.quantidade = p.endereco, p.quantidade
        if erro:
            ev.status = corpo[0]
        elif funcao in (3, 4):
            ev.valores = palavras(corpo[1:])
    return ev


DECODIFICADORES[502] = decodificar_modbus


S7_OPERACAO = {0x04: "leitura", 0x05: "escrita",
               0x28: "controle", 0x29: "controle"}


def decodificar_s7(seg):
    d = seg.payload
    # TPKT: versão 3 e tamanho total igual ao que chegou
    if len(d) < 17 or d[0] != 3:
        return None
    if struct.unpack(">H", d[2:4])[0] != len(d):
        return None
    if d[5] != 0xF0:             # COTP de dados; senão é conexão
        return None
    s7 = d[5 + d[4]:]            # pula TPKT (4) e COTP (1 + d[4])
    rosctr = s7[1]               # 1 = pedido; 2 e 3 = resposta
    if s7[0] != 0x32 or rosctr not in (1, 2, 3):
        return None
    pdu_ref, tam_param, tam_dados = struct.unpack(">HHH", s7[4:10])
    pergunta = rosctr == 1
    inicio = 10 if pergunta else 12   # resposta: +2 bytes de erro
    if len(s7) < inicio:
        return None
    param = s7[inicio:inicio + tam_param]
    dados = s7[inicio + tam_param:inicio + tam_param + tam_dados]
    funcao = param[0] if param else 0
    ev = Evento(seg.ts, seg.ip_origem, seg.ip_destino, "s7",
                "pergunta" if pergunta else "resposta",
                S7_OPERACAO.get(funcao, "outra"), funcao)
    if pergunta:
        # Read/Write Var: o 1o item começa em param[2], 12 bytes
        if funcao in (0x04, 0x05) and len(param) >= 14:
            ev.quantidade, db = struct.unpack(">HH", param[6:10])
            ev.area = f"DB{db}" if param[10] == 0x84 else hex(param[10])
            ev.endereco = int.from_bytes(param[11:14], "big") >> 3
        if funcao == 0x05:
            ev.valores = palavras(dados[4:])
        PENDENTES[("s7", seg.ip_origem, pdu_ref)] = ev
    else:
        p = PENDENTES.pop(("s7", seg.ip_destino, pdu_ref), None)
        if p:
            ev.funcao, ev.operacao, ev.area = p.funcao, p.operacao, p.area
            ev.endereco, ev.quantidade = p.endereco, p.quantidade
        ev.status = struct.unpack(">H", s7[10:12])[0]   # ex.: 0x8104
        if ev.status == 0 and dados and dados[0] != 0xFF:
            ev.status = dados[0]    # erro do item: 0x0A = não existe
        elif ev.status == 0 and ev.funcao == 0x04:
            ev.valores = palavras(dados[4:])
    return ev


DECODIFICADORES[102] = decodificar_s7


if __name__ == "__main__":
    from captura import ler_arquivo
    for seg in ler_arquivo("exemplo.pcap"):
        print(decodificar(seg))
