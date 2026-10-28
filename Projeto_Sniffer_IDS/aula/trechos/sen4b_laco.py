    try:
        while True:
            try:
                seg = fila.get(timeout=1)   # timeout: deixa o Ctrl+C agir
            except queue.Empty:
                continue
            if seg is None:
                break
            ev = decodificar(seg)
            if ev is None:
                contadores["nao_decodificados"] += 1
            else:
                analisar(ev, janela, args.quieto)
    except KeyboardInterrupt:
        pass
