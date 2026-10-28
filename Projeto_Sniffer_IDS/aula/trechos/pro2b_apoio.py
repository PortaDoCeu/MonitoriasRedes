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
