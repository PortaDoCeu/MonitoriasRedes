"""Gera o pacote dos alunos a partir da solução de referência.

Os trechos marcados na solução com

    # >>> ETAPA n | substituto | dica
    ...código da solução...
    # <<<

viram, no pacote do aluno,

    # TODO etapa n: dica
    substituto

Assim o esqueleto nunca diverge da solução testada.

Uso (na pasta Projeto_Planta_MQTT):
    python aula/gerar_pacote_aluno.py
Resultado: aula/projeto_aluno/ e aula/projeto_aluno.zip
"""

import os
import re
import shutil
import stat
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "aula" / "projeto_aluno"

COPIAR = [
    "contrato.py", "config.py", "clp_simulado.py", "config.exemplo.env",
    "requirements.txt", "iniciar.ps1", "parar.ps1",
    "middleware/static", "img", "clp", "aula/Aula.ipynb", "Arquitetura.md", "decisoes",
]
COM_LACUNAS = ["gateway/gateway.py", "middleware/middleware.py"]
# origem na solução -> destino no pacote (o broker do aluno vem com lacunas, etapa 2)
RENOMEAR = {"aula/esqueleto_broker/mosquitto.conf": "broker/mosquitto.conf",
            "aula/esqueleto_broker/acl": "broker/acl"}

INICIO = re.compile(r"^(\s*)# >>> ETAPA (\d) \| (.*?) \| (.*)$")
FIM = re.compile(r"^\s*# <<<\s*$")


def esvaziar(texto):
    saida, dentro = [], False
    for linha in texto.splitlines():
        if dentro:
            if FIM.match(linha):
                dentro = False
            continue
        m = INICIO.match(linha)
        if m:
            recuo, etapa, substituto, dica = m.groups()
            saida.append(f"{recuo}# TODO etapa {etapa}: {dica}")
            saida.append(f"{recuo}{substituto}")
            dentro = True
        else:
            saida.append(linha)
    if dentro:
        raise ValueError("marcador # >>> sem # <<< correspondente")
    return "\n".join(saida) + "\n"


def liberar(funcao, caminho, _erro):
    """O OneDrive marca pastas como somente leitura; tira o atributo e tenta de novo."""
    os.chmod(caminho, stat.S_IWRITE)
    funcao(caminho)


def remover(pasta, tentativas=10):
    """rmtree tolerante ao OneDrive (atributo somente leitura e sincronização em andamento)."""
    for tentativa in range(tentativas):
        if not pasta.exists():
            return
        try:
            shutil.rmtree(pasta, onexc=liberar)
            return
        except PermissionError:
            if tentativa == tentativas - 1:
                raise
            time.sleep(0.5)


def main():
    remover(DESTINO)
    for item in COPIAR:
        origem = RAIZ / item
        alvo = DESTINO / item
        alvo.parent.mkdir(parents=True, exist_ok=True)
        if origem.is_dir():
            shutil.copytree(origem, alvo, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(origem, alvo)
    for origem, destino in RENOMEAR.items():
        alvo = DESTINO / destino
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAIZ / origem, alvo)
    for item in COM_LACUNAS:
        alvo = DESTINO / item
        alvo.parent.mkdir(parents=True, exist_ok=True)
        texto = esvaziar((RAIZ / item).read_text(encoding="utf-8"))
        alvo.write_text(texto, encoding="utf-8")
        print(f"{item}: {texto.count('# TODO etapa')} lacunas")
    zip_final = shutil.make_archive(str(DESTINO), "zip", DESTINO.parent, DESTINO.name)
    print("pacote:", zip_final)


if __name__ == "__main__":
    main()
