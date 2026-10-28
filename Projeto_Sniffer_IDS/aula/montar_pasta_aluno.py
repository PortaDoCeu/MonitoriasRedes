"""Monta a pasta que vai em cada PC do laboratório (e um .zip dela).

    python montar_pasta_aluno.py   -> aula/pasta_aluno/ e aula/pasta_aluno.zip

Conteúdo: exemplo.pcap, carga.pcap, ferramentas/ (gerador de tráfego) e LEIAME.txt.
Os 4 arquivos do sensor NÃO vão: a turma escreve em sala.
"""

import shutil
import subprocess
import sys
from pathlib import Path

AULA = Path(__file__).resolve().parent
PROJETO = AULA.parent
PASTA = AULA / "pasta_aluno"

LEIAME = """Aula: construindo um sensor de tráfego industrial

Nesta pasta:
  exemplo.pcap   tráfego da bancada, com um intruso (usado em todos os testes)
  carga.pcap     100 mil pacotes, para medir o limite do Python
  ferramentas/   gerar_trafego.py conversa com o CLP real (parte ao vivo)

Preparação (no terminal, dentro desta pasta):
  python -m venv .venv
  .venv\\Scripts\\activate
  pip install scapy

Vocês vão criar aqui: captura.py, protocolos.py, regras.py, sensor.py
"""

if PASTA.exists():
    shutil.rmtree(PASTA)
(PASTA / "ferramentas").mkdir(parents=True)

if not (PROJETO / "carga.pcap").exists():
    subprocess.run([sys.executable, "gerar_pcap.py", "--carga", "100000"], cwd=PROJETO / "ferramentas", check=True)
for nome in ("exemplo.pcap", "carga.pcap"):
    shutil.copy(PROJETO / nome, PASTA / nome)
for nome in ("mensagens.py", "gerar_trafego.py"):
    shutil.copy(PROJETO / "ferramentas" / nome, PASTA / "ferramentas" / nome)
(PASTA / "LEIAME.txt").write_text(LEIAME, encoding="utf-8")

shutil.make_archive(str(AULA / "pasta_aluno"), "zip", PASTA)
print("gerado:", PASTA, "e", AULA / "pasta_aluno.zip")
