import argparse
import queue
import threading
import time
from collections import Counter

from captura import capturar, ler_arquivo
from protocolos import decodificar
from regras import Janela, avaliar

contadores = Counter()
fila = queue.Queue(maxsize=1000)    # em C: xQueueCreate(1000, ...)


def ao_receber(seg):                # roda na thread de captura
    contadores["capturados"] += 1
    try:
        fila.put_nowait(seg)
    except queue.Full:              # fila cheia: descarta e conta
        contadores["descartados"] += 1


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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--interface")
    p.add_argument("--arquivo")
    p.add_argument("--quieto", action="store_true")
    args = p.parse_args()
    iniciar(args)
    janela, inicio = Janela(), time.perf_counter()
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
    segundos = time.perf_counter() - inicio
    print(dict(contadores))
    print(f"{contadores['capturados'] / segundos:.0f} segmentos/s")


if __name__ == "__main__":
    main()
