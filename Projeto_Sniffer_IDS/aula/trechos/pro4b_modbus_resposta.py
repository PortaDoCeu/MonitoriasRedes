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
