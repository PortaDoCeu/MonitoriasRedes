"""Etapa 1: captura.

Pega pacotes da placa de rede (ao vivo) ou de um arquivo .pcap e entrega só o que
interessa ao sensor: segmentos TCP com dados nas portas industriais.

Em C (ESP32): módulos eth_cap, pool e parse_l2l4. Lá não existe Scapy nem filtro BPF:
o driver entrega o quadro cru e cada cabeçalho (Ethernet, IP, TCP) é conferido à mão.
"""

from dataclasses import dataclass

from scapy.all import IP, TCP, PcapReader, sniff

PORTAS = {502, 102}                          # 502 = Modbus TCP, 102 = S7comm (ISO-on-TCP)
FILTRO = "tcp port 502 or tcp port 102"      # filtro BPF, aplicado pelo Npcap


@dataclass
class Segmento:
    """O que sobra de um pacote depois de tirar Ethernet, IP e TCP."""
    ts: float
    ip_origem: str
    ip_destino: str
    porta_origem: int
    porta_destino: int
    payload: bytes


def para_segmento(pacote):
    """Converte um pacote do Scapy em Segmento. Devolve None se não houver dados TCP."""
    if IP not in pacote or TCP not in pacote:
        return None
    ip, tcp = pacote[IP], pacote[TCP]

    # Tamanho real dos dados: o que o IP diz, menos os cabeçalhos IP e TCP.
    # Assim ignoramos o enchimento (padding) que a Ethernet põe em quadros pequenos.
    tamanho = ip.len - ip.ihl * 4 - tcp.dataofs * 4
    if tamanho <= 0:
        return None                          # SYN, ACK puro, FIN: sem dados

    dados = bytes(tcp.payload)[:tamanho]
    return Segmento(float(pacote.time), ip.src, ip.dst, tcp.sport, tcp.dport, dados)


def ler_arquivo(caminho):
    """Lê um .pcap e produz um Segmento por pacote interessante."""
    with PcapReader(caminho) as leitor:
        for pacote in leitor:
            seg = para_segmento(pacote)
            if seg and (seg.porta_origem in PORTAS or seg.porta_destino in PORTAS):
                yield seg


def capturar(interface, ao_receber):
    """Captura ao vivo e chama ao_receber(segmento) para cada pacote. Não retorna."""
    def tratar(pacote):
        seg = para_segmento(pacote)
        if seg:
            ao_receber(seg)

    sniff(iface=interface, filter=FILTRO, prn=tratar, store=False)
