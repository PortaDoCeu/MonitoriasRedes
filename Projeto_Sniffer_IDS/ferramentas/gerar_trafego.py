"""Gera tráfego real entre o PC e um CLP da bancada, para o sensor capturar.

Fala Modbus TCP e S7comm direto por socket, com as mesmas mensagens que o sensor decodifica.

    python gerar_trafego.py --clp 192.168.0.11                  # só leituras (Modbus e S7), 1 por segundo
    python gerar_trafego.py --clp 192.168.0.11 --sem-s7         # só Modbus
    python gerar_trafego.py --clp 192.168.0.11 --escrever 10 1500   # UMA escrita (demonstração do intruso)

Pré-requisitos no CLP: MB_SERVER na porta 502 para o Modbus; PUT/GET permitido e um DB1
não otimizado com pelo menos 20 bytes para o S7. A escrita só acontece com --escrever:
use um registrador de teste, nunca um que comande saída do CLP.
"""

import argparse
import socket
import struct
import time

import mensagens as m


def receber_exato(sock, n):
    dados = b""
    while len(dados) < n:
        parte = sock.recv(n - len(dados))
        if not parte:
            raise ConnectionError("o CLP fechou a conexão")
        dados += parte
    return dados


def receber_modbus(sock):
    cab = receber_exato(sock, 6)
    return cab + receber_exato(sock, struct.unpack(">H", cab[4:6])[0])


def receber_tpkt(sock):
    cab = receber_exato(sock, 4)
    return cab + receber_exato(sock, struct.unpack(">H", cab[2:4])[0] - 4)


def conectar_s7(clp):
    sock = socket.create_connection((clp, 102), timeout=3)
    sock.sendall(m.COTP_CONECTAR)
    receber_tpkt(sock)
    sock.sendall(m.s7_setup())
    receber_tpkt(sock)
    return sock


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--clp", required=True)
    p.add_argument("--sem-s7", action="store_true")
    p.add_argument("--escrever", nargs=2, type=int, metavar=("ENDERECO", "VALOR"))
    args = p.parse_args()

    modbus = socket.create_connection((args.clp, 502), timeout=3)
    if args.escrever:
        endereco, valor = args.escrever
        modbus.sendall(m.modbus_escrever(1, endereco, valor))
        print("resposta:", receber_modbus(modbus).hex(" "))
        return

    s7 = None if args.sem_s7 else conectar_s7(args.clp)
    n = 0
    while True:
        n += 1
        modbus.sendall(m.modbus_ler(n % 65536, 0, 10))
        print("modbus:", receber_modbus(modbus).hex(" "))
        if s7:
            s7.sendall(m.s7_ler_db(n % 65536, 1, 0, 20))
            print("s7:    ", receber_tpkt(s7).hex(" "))
        time.sleep(1)


if __name__ == "__main__":
    main()
