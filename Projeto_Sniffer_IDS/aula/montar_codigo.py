"""Junta os trechos dos slides nos 4 arquivos da aula, na ordem final.

    python montar_codigo.py      -> gera aula/codigo/*.py e copia o exemplo.pcap

A ordem de DIGITAÇÃO em sala é a dos slides; a ordem no ARQUIVO é a daqui
(o S7 entra antes do bloco de teste de protocolos.py).
"""

import shutil
from pathlib import Path

AULA = Path(__file__).resolve().parent
TRECHOS = AULA / "trechos"
DESTINO = AULA / "codigo"

ORDEM = {
    "captura.py": ["cap1_segmento", "cap2_para_segmento", "cap3_ler_capturar", "cap4_teste"],
    "protocolos.py": ["pro1_evento", "pro2a_str", "pro2b_apoio", "pro3_modbus_cabecalho",
                      "pro4a_modbus_pergunta", "pro4b_modbus_resposta", "pro6_s7_camadas",
                      "pro7a_s7_cabecalho", "pro7b_s7_pergunta", "pro8_s7_resposta",
                      "pro5_teste"],
    "regras.py": ["reg1a_inventario", "reg1b_regras", "reg2_avaliar", "reg3_janela", "reg4_teste"],
    "sensor.py": ["sen1a_imports", "sen1b_ao_receber", "sen2_iniciar", "sen3_analisar", "sen4a_main", "sen4b_laco",
                  "sen5_fim"],
}

# Trechos que continuam a função ou classe do trecho anterior: sem linhas em branco extras.
CONTINUACAO = {"pro2a_str", "pro4a_modbus_pergunta", "pro4b_modbus_resposta", "pro7a_s7_cabecalho",
               "pro7b_s7_pergunta", "pro8_s7_resposta",
               "sen4b_laco", "sen5_fim"}

DESTINO.mkdir(exist_ok=True)
for arquivo, trechos in ORDEM.items():
    partes = []
    for nome in trechos:
        texto = (TRECHOS / f"{nome}.py").read_text(encoding="utf-8").rstrip("\n")
        if partes:
            partes.append("\n" if nome in CONTINUACAO else "\n\n\n")
        partes.append(texto)
    (DESTINO / arquivo).write_text("".join(partes) + "\n", encoding="utf-8")
    print("gerado:", DESTINO / arquivo)

shutil.copy(AULA.parent / "exemplo.pcap", DESTINO / "exemplo.pcap")
