if __name__ == "__main__":
    for seg in ler_arquivo("exemplo.pcap"):
        print(seg.ip_origem, "->", seg.ip_destino,
              seg.porta_destino, seg.payload.hex(" "))
