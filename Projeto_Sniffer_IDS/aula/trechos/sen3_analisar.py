def analisar(ev, janela, quieto):
    if not quieto:
        print(ev)
    for codigo, nivel, texto in avaliar(ev):
        contadores["alertas"] += 1
        print(f"  !!! {codigo} {nivel}: {texto}")
        print(f"      {ev}")
    resumo = janela.adicionar(ev)
    if resumo and not quieto:
        print("--- últimos 10 s:")
        for chave, n in resumo.items():
            print("   ", *chave, n)
