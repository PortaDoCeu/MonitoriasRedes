def para_segmento(pacote):
    if IP not in pacote or TCP not in pacote:
        return None
    ip, tcp = pacote[IP], pacote[TCP]
    # tamanho dos dados = total do IP - cabeçalho IP - cabeçalho TCP
    tamanho = ip.len - ip.ihl * 4 - tcp.dataofs * 4
    if tamanho <= 0:
        return None    # SYN, ACK puro, FIN: sem dados
    dados = bytes(tcp.payload)[:tamanho]
    return Segmento(float(pacote.time), ip.src, ip.dst,
                    tcp.sport, tcp.dport, dados)
