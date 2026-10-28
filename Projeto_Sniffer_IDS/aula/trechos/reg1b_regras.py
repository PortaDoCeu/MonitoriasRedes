def controle_do_clp(ev):
    return ev.direcao == "pergunta" and ev.operacao == "controle"


def ip_desconhecido(ev):
    return ev.origem not in ATIVOS


def resposta_de_erro(ev):
    return ev.direcao == "resposta" and ev.status != 0
