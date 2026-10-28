def ler_arquivo(caminho):
    for pacote in PcapReader(caminho):
        seg = para_segmento(pacote)
        if seg and (seg.porta_origem in PORTAS
                    or seg.porta_destino in PORTAS):
            yield seg


def capturar(interface, ao_receber):
    def tratar(pacote):
        seg = para_segmento(pacote)
        if seg:
            ao_receber(seg)
    sniff(iface=interface, filter="tcp port 502 or tcp port 102",
          prn=tratar, store=False)
