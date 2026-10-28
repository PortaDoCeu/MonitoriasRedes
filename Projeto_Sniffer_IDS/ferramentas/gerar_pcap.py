"""Gera arquivos .pcap de exemplo, sem precisar de bancada.

    python gerar_pcap.py                 -> ../exemplo.pcap (cenário da aula, ~40 pacotes)
    python gerar_pcap.py --carga 200000  -> ../carga.pcap   (para medir o limite do Python)

Cenário (IPs iguais aos de sensor/regras.py):
  - estação de engenharia .29 lê holding registers do CLP .11 (Modbus) a cada segundo;
  - CLP .11 lê 20 bytes do DB1 do CLP .12 (S7, o PUT/GET da aula);
  - aos 6 s, um intruso .50 escreve no CLP .11 (Modbus função 6);
  - aos 8 s, o intruso tenta ler o CLP .11 por S7 e recebe 0x8104 (PUT/GET não permitido);
  - aos 9 s, o intruso manda PLC STOP para o CLP .12.
"""

import argparse
from pathlib import Path

from scapy.all import IP, TCP, Ether, Raw, wrpcap

import mensagens as m

RAIZ = Path(__file__).resolve().parent.parent
MAC = {"192.168.0.11": "28:63:36:89:ed:31", "192.168.0.12": "28:63:36:81:cd:6f",
       "192.168.0.29": "d0:ad:08:ba:c8:d6", "192.168.0.50": "02:00:00:00:00:50"}


class Conversa:
    """Uma conexão TCP entre cliente e servidor; cuida de portas e números de sequência."""

    def __init__(self, cliente, servidor, porta, porta_cliente):
        self.cliente, self.servidor, self.porta, self.pc = cliente, servidor, porta, porta_cliente
        self.seq_c, self.seq_s = 1000, 5000

    def pacote(self, t, dados, do_cliente=True):
        if do_cliente:
            ip = IP(src=self.cliente, dst=self.servidor)
            tcp = TCP(sport=self.pc, dport=self.porta, flags="PA", seq=self.seq_c, ack=self.seq_s)
            self.seq_c += len(dados)
            eth = Ether(src=MAC[self.cliente], dst=MAC[self.servidor])
        else:
            ip = IP(src=self.servidor, dst=self.cliente)
            tcp = TCP(sport=self.porta, dport=self.pc, flags="PA", seq=self.seq_s, ack=self.seq_c)
            self.seq_s += len(dados)
            eth = Ether(src=MAC[self.servidor], dst=MAC[self.cliente])
        p = eth / ip / tcp / Raw(dados)
        p.time = t
        return p


def cenario_aula(t0=1_800_000_000.0):
    eng = Conversa("192.168.0.29", "192.168.0.11", 502, 50101)
    putget = Conversa("192.168.0.11", "192.168.0.12", 102, 2001)
    intruso_mb = Conversa("192.168.0.50", "192.168.0.11", 502, 40001)
    intruso_s7 = Conversa("192.168.0.50", "192.168.0.11", 102, 40002)
    intruso_stop = Conversa("192.168.0.50", "192.168.0.12", 102, 40003)

    pacotes = []
    for s in range(12):
        t = t0 + s
        temperatura = 250 + s                                  # valor que muda: série temporal
        pacotes.append(eng.pacote(t, m.modbus_ler(s + 1, 0, 10)))
        pacotes.append(eng.pacote(t + 0.004, m.modbus_resposta_leitura(s + 1, [temperatura, 1, 0, 0, 0, 0, 0, 0, 0, 0]), False))
        pacotes.append(putget.pacote(t + 0.5, m.s7_ler_db(s + 1, 1, 0, 20)))
        pacotes.append(putget.pacote(t + 0.503, m.s7_resposta_leitura(s + 1, bytes([0x00, 0x52]) + bytes(18)), False))

        if s == 6:
            pacotes.append(intruso_mb.pacote(t + 0.7, m.modbus_escrever(1, 10, 1500)))
            pacotes.append(intruso_mb.pacote(t + 0.703, m.modbus_escrever(1, 10, 1500), False))
        if s == 8:
            pacotes.append(intruso_s7.pacote(t + 0.7, m.s7_ler_db(1, 1, 0, 20)))
            pacotes.append(intruso_s7.pacote(t + 0.703, m.s7_resposta_erro(1, 0x8104), False))
        if s == 9:
            pacotes.append(intruso_stop.pacote(t + 0.7, m.s7_parar_clp(1)))
    return sorted(pacotes, key=lambda p: p.time)


def carga(n, t0=1_800_000_000.0):
    """n pacotes de leitura Modbus pergunta/resposta, 10 000 por segundo."""
    eng = Conversa("192.168.0.29", "192.168.0.11", 502, 50101)
    pacotes = []
    for i in range(n // 2):
        t = t0 + i / 5000
        pacotes.append(eng.pacote(t, m.modbus_ler(i % 65536, 0, 10)))
        pacotes.append(eng.pacote(t + 0.0001, m.modbus_resposta_leitura(i % 65536, [i % 1000] + [0] * 9), False))
    return pacotes


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--carga", type=int, help="gera carga.pcap com N pacotes")
    args = p.parse_args()
    if args.carga:
        wrpcap(str(RAIZ / "carga.pcap"), carga(args.carga))
        print("gerado:", RAIZ / "carga.pcap")
    else:
        wrpcap(str(RAIZ / "exemplo.pcap"), cenario_aula())
        print("gerado:", RAIZ / "exemplo.pcap")
