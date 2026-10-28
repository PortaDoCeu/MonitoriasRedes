def main():
    p = argparse.ArgumentParser()
    p.add_argument("--interface")
    p.add_argument("--arquivo")
    p.add_argument("--quieto", action="store_true")
    args = p.parse_args()
    iniciar(args)
    janela, inicio = Janela(), time.perf_counter()
