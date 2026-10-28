if __name__ == "__main__":
    from captura import ler_arquivo
    for seg in ler_arquivo("exemplo.pcap"):
        print(decodificar(seg))
