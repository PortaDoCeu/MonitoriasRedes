"""Leitura do config.env (ADR-025).

Formato: uma linha CHAVE=valor por configuração; linhas com # são comentários.
Variáveis de ambiente com o mesmo nome têm prioridade sobre o arquivo
(útil para testes e para rodar dois gateways na mesma máquina).
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ARQUIVO_PADRAO = RAIZ / "config.env"


def configurar_log(programa):
    """Console em INFO e arquivo logs/<programa>.log em DEBUG, rotativo (ADR-026)."""
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8", errors="replace")
    pasta = RAIZ / "logs"
    pasta.mkdir(exist_ok=True)
    formato = logging.Formatter(f"%(asctime)s %(levelname)s [{programa}] %(message)s", "%H:%M:%S")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formato)
    arquivo = RotatingFileHandler(pasta / f"{programa}.log", maxBytes=5_000_000,
                                  backupCount=3, encoding="utf-8")
    arquivo.setLevel(logging.DEBUG)
    arquivo.setFormatter(formato)
    raiz = logging.getLogger()
    raiz.setLevel(logging.DEBUG)
    raiz.handlers[:] = [console, arquivo]
    for ruidoso in ("pymodbus", "uvicorn.access", "asyncio"):
        logging.getLogger(ruidoso).setLevel(logging.WARNING)
    return logging.getLogger(programa)


def ler_arquivo(caminho):
    valores = {}
    if not caminho.exists():
        return valores
    # utf-8-sig: aceita o BOM que o Bloco de Notas e o PowerShell 5.1 gravam
    for numero, linha in enumerate(caminho.read_text(encoding="utf-8-sig").splitlines(), 1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        if "=" not in linha:
            raise ValueError(f"{caminho.name}, linha {numero}: esperado CHAVE=valor")
        chave, valor = linha.split("=", 1)
        valores[chave.strip()] = valor.strip()
    return valores


def carregar(obrigatorias, caminho=None):
    """Devolve um dicionário com a configuração; encerra o programa se faltar uma chave."""
    caminho = Path(caminho) if caminho else ARQUIVO_PADRAO
    valores = ler_arquivo(caminho)
    for chave, valor in os.environ.items():
        if chave in obrigatorias or chave in valores:
            valores[chave] = valor
    faltando = [c for c in obrigatorias if not valores.get(c)]
    if faltando:
        sys.exit(f"Configuração incompleta em {caminho}: faltam {', '.join(faltando)}. "
                 f"Copie config.exemplo.env para config.env e preencha.")
    return valores
