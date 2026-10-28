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
