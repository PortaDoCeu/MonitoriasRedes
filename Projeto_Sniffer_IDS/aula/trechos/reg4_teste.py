if __name__ == "__main__":
    from captura import ler_arquivo
    from protocolos import decodificar
    for seg in ler_arquivo("exemplo.pcap"):
        ev = decodificar(seg)
        if ev:
            for alerta in avaliar(ev):
                print(alerta, ev)
