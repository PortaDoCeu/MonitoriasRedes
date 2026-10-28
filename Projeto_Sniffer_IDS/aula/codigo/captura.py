from dataclasses import dataclass

from scapy.all import IP, TCP, PcapReader, sniff

PORTAS = {502, 102}   # 502 = Modbus TCP, 102 = S7comm


@dataclass
class Segmento:
    ts: float          # hora da captura, em segundos
    ip_origem: str
    ip_destino: str
    porta_origem: int
    porta_destino: int
    payload: bytes     # os dados que o TCP carrega


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


if __name__ == "__main__":
    for seg in ler_arquivo("exemplo.pcap"):
        print(seg.ip_origem, "->", seg.ip_destino,
              seg.porta_destino, seg.payload.hex(" "))
