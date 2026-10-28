def do_arquivo(caminho):
    for seg in ler_arquivo(caminho):
        contadores["capturados"] += 1
        fila.put(seg)               # do arquivo: espera, não descarta
    fila.put(None)                  # aviso de fim


def iniciar(args):
    if args.arquivo:
        alvo, parametros = do_arquivo, (args.arquivo,)
    else:
        alvo, parametros = capturar, (args.interface, ao_receber)
    threading.Thread(target=alvo, args=parametros, daemon=True).start()
