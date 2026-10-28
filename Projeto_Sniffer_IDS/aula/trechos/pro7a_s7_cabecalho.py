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
