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
