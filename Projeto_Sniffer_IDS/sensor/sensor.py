"""Etapa 5: ligar tudo.

Uma thread captura e põe os segmentos numa fila de tamanho limitado. O laço principal
tira da fila, decodifica, avalia as regras e soma na janela. Se a fila enche, o
segmento é descartado e contado: o sensor nunca trava, mas avisa o que perdeu.

Uso (no terminal como administrador para captura ao vivo):
    python sensor.py --interface "Ethernet"
    python sensor.py --arquivo ../exemplo.pcap
    python sensor.py --arquivo ../carga.pcap --medir

Em C (ESP32): app_main cria duas tarefas do FreeRTOS (captura e análise, em núcleos
diferentes), a fila com xQueueCreate e a tarefa de saúde que publica os contadores.
"""

import argparse
import csv
import queue
import threading
import time
from collections import Counter

from captura import capturar, ler_arquivo
from protocolos import decodificar
from regras import Janela, avaliar

TAMANHO_FILA = 1000
contadores = Counter()


def produzir_ao_vivo(interface, fila):
    def ao_receber(seg):
        contadores["capturados"] += 1
        try:
            fila.put_nowait(seg)
        except queue.Full:
            contadores["descartados_fila_cheia"] += 1
    capturar(interface, ao_receber)


def produzir_do_arquivo(caminho, fila):
    for seg in ler_arquivo(caminho):
        contadores["capturados"] += 1
        fila.put(seg)                       # do arquivo, espera em vez de descartar
    fila.put(None)                          # aviso de fim


def imprimir_janela(resumo):
    print(f"\n--- janela de {time.strftime('%H:%M:%S', time.localtime(resumo['inicio']))} ---")
    for (origem, destino, protocolo, operacao), n in resumo["contagem"].most_common():
        print(f"  {origem:>15} -> {destino:<15} {protocolo:6} {operacao:11} {n:5}")
    for (servidor, area, endereco), valores in resumo["valores"].items():
        print(f"  valores {servidor} {area} end={endereco}: {valores}")
    print()


def main():
    p = argparse.ArgumentParser(description="Sensor passivo de tráfego industrial")
    origem = p.add_mutually_exclusive_group(required=True)
    origem.add_argument("--interface", help='placa de rede, ex.: "Ethernet"')
    origem.add_argument("--arquivo", help="arquivo .pcap")
    p.add_argument("--quieto", action="store_true", help="não imprime cada evento")
    p.add_argument("--medir", action="store_true", help="mede pacotes por segundo (use com --quieto)")
    args = p.parse_args()

    fila = queue.Queue(maxsize=TAMANHO_FILA)
    if args.interface:
        alvo, parametro = produzir_ao_vivo, args.interface
    else:
        alvo, parametro = produzir_do_arquivo, args.arquivo
    threading.Thread(target=alvo, args=(parametro, fila), daemon=True).start()

    janela = Janela(segundos=10)
    inicio = time.perf_counter()
    with open("alertas.csv", "a", newline="", encoding="utf-8") as arquivo_csv:
        alertas_csv = csv.writer(arquivo_csv)
        try:
            while True:
                seg = fila.get()
                if seg is None:
                    break
                ev = decodificar(seg)
                if ev is None:
                    contadores["nao_decodificados"] += 1
                    continue
                contadores["eventos"] += 1
                if not args.quieto:
                    print(ev)

                for alerta in avaliar(ev):
                    contadores["alertas"] += 1
                    print(alerta)
                    alertas_csv.writerow([ev.ts, alerta.regra, alerta.severidade, alerta.descricao, str(ev)])

                resumo = janela.adicionar(ev)
                if resumo and not args.quieto:
                    imprimir_janela(resumo)
        except KeyboardInterrupt:
            pass

    duracao = time.perf_counter() - inicio
    print("\nContadores:", dict(contadores))
    if args.medir and duracao > 0:
        print(f"Processou {contadores['capturados'] / duracao:,.0f} segmentos/s "
              f"({contadores['capturados']} em {duracao:.1f} s)")


if __name__ == "__main__":
    main()
