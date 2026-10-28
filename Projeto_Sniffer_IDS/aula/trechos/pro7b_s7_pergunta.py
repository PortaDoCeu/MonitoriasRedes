    if pergunta:
        # Read/Write Var: o 1o item começa em param[2], 12 bytes
        if funcao in (0x04, 0x05) and len(param) >= 14:
            ev.quantidade, db = struct.unpack(">HH", param[6:10])
            ev.area = f"DB{db}" if param[10] == 0x84 else hex(param[10])
            ev.endereco = int.from_bytes(param[11:14], "big") >> 3
        if funcao == 0x05:
            ev.valores = palavras(dados[4:])
        PENDENTES[("s7", seg.ip_origem, pdu_ref)] = ev
