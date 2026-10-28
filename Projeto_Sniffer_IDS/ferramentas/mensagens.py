"""Mensagens Modbus TCP e S7comm montadas byte a byte.

Usadas pelo gerador de tráfego (CLP real), pelo gerador de .pcap e pelos testes.
São o "outro lado" dos decodificadores de sensor/protocolos.py.
"""

import struct

# ---------------------------------------------------------------- Modbus TCP


def _mbap(transacao, pdu, unidade=1):
    """Cabeçalho MBAP: transação, protocolo (0), tamanho (unidade + PDU), unidade."""
    return struct.pack(">HHHB", transacao, 0, len(pdu) + 1, unidade) + pdu


def modbus_ler(transacao, endereco, quantidade):
    """Função 3: ler holding registers."""
    return _mbap(transacao, struct.pack(">BHH", 3, endereco, quantidade))


def modbus_resposta_leitura(transacao, valores):
    dados = struct.pack(f">{len(valores)}H", *valores)
    return _mbap(transacao, bytes([3, len(dados)]) + dados)


def modbus_escrever(transacao, endereco, valor):
    """Função 6: escrever um holding register. A resposta é o eco da pergunta."""
    return _mbap(transacao, struct.pack(">BHH", 6, endereco, valor))


def modbus_excecao(transacao, funcao, codigo):
    """Resposta de erro: função com o bit 7 ligado + código de exceção."""
    return _mbap(transacao, bytes([funcao | 0x80, codigo]))


# ---------------------------------------------------------------- S7comm (TPKT + COTP + S7)


def _tpkt_cotp(s7):
    cotp = bytes([0x02, 0xF0, 0x80])                     # COTP de dados (DT), último fragmento
    return struct.pack(">BBH", 3, 0, 4 + len(cotp) + len(s7)) + cotp + s7


def _s7_pedido(pdu_ref, param, dados=b""):
    return _tpkt_cotp(struct.pack(">BBHHHH", 0x32, 1, 0, pdu_ref, len(param), len(dados)) + param + dados)


def _s7_resposta(pdu_ref, param, dados=b"", erro=0):
    cab = struct.pack(">BBHHHHH", 0x32, 3, 0, pdu_ref, len(param), len(dados), erro)
    return _tpkt_cotp(cab + param + dados)


# Pedido de conexão COTP: TSAP local 01.00, remoto 03.01 (rack 0, slot 1 do S7-1200)
COTP_CONECTAR = bytes([0x03, 0x00, 0x00, 0x16, 0x11, 0xE0, 0x00, 0x00, 0x00, 0x01, 0x00,
                       0xC0, 0x01, 0x0A, 0xC1, 0x02, 0x01, 0x00, 0xC2, 0x02, 0x03, 0x01])


def s7_setup(pdu_ref=0):
    """Setup Communication: negocia o tamanho da PDU (240 bytes)."""
    return _s7_pedido(pdu_ref, bytes([0xF0, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0xF0]))


def _item_db(db, endereco_byte, quantidade_bytes):
    """Item de 12 bytes: 0x12, 0x0A, 0x10, tipo BYTE, quantidade, DB, área DB (0x84), endereço em bits."""
    return (bytes([0x12, 0x0A, 0x10, 0x02]) + struct.pack(">HH", quantidade_bytes, db)
            + bytes([0x84]) + (endereco_byte * 8).to_bytes(3, "big"))


def s7_ler_db(pdu_ref, db, endereco_byte, quantidade_bytes):
    return _s7_pedido(pdu_ref, bytes([0x04, 0x01]) + _item_db(db, endereco_byte, quantidade_bytes))


def s7_resposta_leitura(pdu_ref, dados_lidos):
    item = bytes([0xFF, 0x04]) + struct.pack(">H", len(dados_lidos) * 8) + dados_lidos
    return _s7_resposta(pdu_ref, bytes([0x04, 0x01]), item)


def s7_escrever_db(pdu_ref, db, endereco_byte, dados):
    item = bytes([0x00, 0x04]) + struct.pack(">H", len(dados) * 8) + dados
    return _s7_pedido(pdu_ref, bytes([0x05, 0x01]) + _item_db(db, endereco_byte, len(dados)), item)


def s7_resposta_erro(pdu_ref, erro):
    """Resposta sem parâmetros, só com classe e código de erro (ex.: 0x8104)."""
    return _s7_resposta(pdu_ref, b"", erro=erro)


def s7_parar_clp(pdu_ref):
    """PLC Stop (função 0x29) com o serviço P_PROGRAM."""
    return _s7_pedido(pdu_ref, bytes([0x29, 0, 0, 0, 0, 0, 9]) + b"P_PROGRAM")
