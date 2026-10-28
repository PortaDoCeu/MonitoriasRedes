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
