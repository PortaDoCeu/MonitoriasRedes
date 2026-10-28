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
