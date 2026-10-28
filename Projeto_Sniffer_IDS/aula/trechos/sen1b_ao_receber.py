def ao_receber(seg):                # roda na thread de captura
    contadores["capturados"] += 1
    try:
        fila.put_nowait(seg)
    except queue.Full:              # fila cheia: descarta e conta
        contadores["descartados"] += 1
