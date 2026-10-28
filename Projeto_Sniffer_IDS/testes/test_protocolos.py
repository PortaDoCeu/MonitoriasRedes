"""Testes dos decodificadores e das regras, sem rede e sem bancada.

    python -m unittest discover -s testes -v      (na pasta Projeto_Sniffer_IDS)
"""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RAIZ / "sensor"), str(RAIZ / "ferramentas")]

import mensagens as m                                   # noqa: E402
from captura import Segmento                            # noqa: E402
from protocolos import PENDENTES, decodificar           # noqa: E402
from regras import avaliar, ultimo_aviso                # noqa: E402

ENG, CLP_A, CLP_B, INTRUSO = "192.168.0.29", "192.168.0.11", "192.168.0.12", "192.168.0.50"


def pergunta(cliente, servidor, porta, dados, ts=1.0):
    return Segmento(ts, cliente, servidor, 50000, porta, dados)


def resposta(cliente, servidor, porta, dados, ts=1.1):
    return Segmento(ts, servidor, cliente, porta, 50000, dados)


class TestModbus(unittest.TestCase):
    def setUp(self):
        PENDENTES.clear()

    def test_leitura_casa_pergunta_e_resposta(self):
        ev = decodificar(pergunta(ENG, CLP_A, 502, m.modbus_ler(7, 0, 10)))
        self.assertEqual((ev.operacao, ev.area, ev.endereco, ev.quantidade), ("leitura", "holding", 0, 10))

        ev = decodificar(resposta(ENG, CLP_A, 502, m.modbus_resposta_leitura(7, [250, 1] + [0] * 8)))
        self.assertEqual(ev.direcao, "resposta")
        self.assertEqual((ev.endereco, ev.quantidade), (0, 10))      # veio da pergunta
        self.assertEqual(ev.valores, [250, 1, 0, 0])

    def test_escrita_simples(self):
        ev = decodificar(pergunta(INTRUSO, CLP_A, 502, m.modbus_escrever(1, 10, 1500)))
        self.assertEqual((ev.operacao, ev.endereco, ev.valores), ("escrita", 10, [1500]))

    def test_excecao(self):
        decodificar(pergunta(ENG, CLP_A, 502, m.modbus_ler(3, 9999, 1)))
        ev = decodificar(resposta(ENG, CLP_A, 502, m.modbus_excecao(3, 3, 2)))
        self.assertEqual((ev.funcao, ev.status), (3, 2))             # 2 = endereço ilegal

    def test_mensagem_cortada_nao_decodifica(self):
        dados = m.modbus_ler(1, 0, 10)
        self.assertIsNone(decodificar(pergunta(ENG, CLP_A, 502, dados[:-2])))

    def test_tamanho_mentiroso_nao_decodifica(self):
        dados = bytearray(m.modbus_ler(1, 0, 10))
        dados[4:6] = (200).to_bytes(2, "big")                        # diz ter 200 bytes
        self.assertIsNone(decodificar(pergunta(ENG, CLP_A, 502, bytes(dados))))


class TestS7(unittest.TestCase):
    def setUp(self):
        PENDENTES.clear()

    def test_leitura_db_do_putget(self):
        ev = decodificar(pergunta(CLP_A, CLP_B, 102, m.s7_ler_db(5, 1, 0, 20)))
        self.assertEqual((ev.protocolo, ev.operacao, ev.area, ev.endereco, ev.quantidade),
                         ("s7", "leitura", "DB1", 0, 20))

        ev = decodificar(resposta(CLP_A, CLP_B, 102, m.s7_resposta_leitura(5, bytes([0, 0x52]) + bytes(18))))
        self.assertEqual((ev.area, ev.quantidade, ev.status), ("DB1", 20, 0))
        self.assertEqual(ev.valores[0], 0x52)

    def test_putget_desabilitado(self):
        decodificar(pergunta(INTRUSO, CLP_A, 102, m.s7_ler_db(9, 1, 0, 20)))
        ev = decodificar(resposta(INTRUSO, CLP_A, 102, m.s7_resposta_erro(9, 0x8104)))
        self.assertEqual((ev.operacao, ev.area, ev.status), ("leitura", "DB1", 0x8104))

    def test_escrita_db(self):
        ev = decodificar(pergunta(INTRUSO, CLP_B, 102, m.s7_escrever_db(2, 1, 4, bytes([0x05, 0xDC]))))
        self.assertEqual((ev.operacao, ev.area, ev.endereco, ev.valores), ("escrita", "DB1", 4, [1500]))

    def test_parar_clp(self):
        ev = decodificar(pergunta(INTRUSO, CLP_B, 102, m.s7_parar_clp(1)))
        self.assertEqual((ev.funcao, ev.operacao), (0x29, "controle"))

    def test_pedido_de_conexao_nao_e_evento(self):
        self.assertIsNone(decodificar(pergunta(ENG, CLP_A, 102, m.COTP_CONECTAR)))


class TestRegras(unittest.TestCase):
    def setUp(self):
        PENDENTES.clear()
        ultimo_aviso.clear()

    def codigos(self, seg):
        return [a.regra for a in avaliar(decodificar(seg))]

    def test_leitura_normal_nao_alerta(self):
        self.assertEqual(self.codigos(pergunta(ENG, CLP_A, 502, m.modbus_ler(1, 0, 10))), [])

    def test_intruso_escrevendo(self):
        self.assertEqual(self.codigos(pergunta(INTRUSO, CLP_A, 502, m.modbus_escrever(1, 10, 1500))),
                         ["R01", "R03"])

    def test_stop_vindo_da_engenharia_tambem_alerta(self):
        self.assertEqual(self.codigos(pergunta(ENG, CLP_B, 102, m.s7_parar_clp(1))), ["R02"])

    def test_nao_repete_alerta_seguido(self):
        seg = pergunta(INTRUSO, CLP_A, 502, m.modbus_escrever(1, 10, 1500), ts=100.0)
        self.assertTrue(self.codigos(seg))
        seg.ts = 101.0
        self.assertEqual(self.codigos(seg), [])


if __name__ == "__main__":
    unittest.main()
