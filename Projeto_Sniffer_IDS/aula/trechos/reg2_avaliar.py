REGRAS = [
    ("R01", "ALTA", "escrita de quem não pode escrever",
     escrita_nao_autorizada),
    ("R02", "CRITICA", "comando de controle no CLP", controle_do_clp),
    ("R03", "ALTA", "IP fora do inventário", ip_desconhecido),
    ("R04", "MEDIA", "resposta de erro", resposta_de_erro),
]


def avaliar(ev):
    alertas = []
    for codigo, nivel, texto, regra in REGRAS:
        if regra(ev):
            alertas.append((codigo, nivel, texto))
    return alertas
