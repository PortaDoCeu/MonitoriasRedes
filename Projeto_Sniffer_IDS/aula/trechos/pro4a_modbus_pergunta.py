    ev = Evento(seg.ts, seg.ip_origem, seg.ip_destino, "modbus",
                "pergunta" if pergunta else "resposta",
                MODBUS_OPERACAO.get(funcao, "outra"), funcao)
    if pergunta:
        if len(corpo) >= 4:
            ev.endereco, ev.quantidade = struct.unpack(">HH", corpo[:4])
        if funcao in (5, 6):     # escrita simples: o 2o campo é o valor
            ev.valores, ev.quantidade = [ev.quantidade], 1
        PENDENTES[("modbus", seg.ip_origem, transacao)] = ev
