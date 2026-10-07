"""Pós-processa o .pptx: cada linha das notas do apresentador vira um parágrafo próprio.

O pptxgenjs grava a nota inteira num único <a:t> com quebras de linha dentro,
que o PowerPoint pode exibir como uma linha só. Aqui cada linha vira um <a:p>,
e o idioma passa a pt-BR (correção ortográfica em português).

Uso: python separar_paragrafos.py ../slides_projeto.pptx
"""

import re
import shutil
import sys
import zipfile
from pathlib import Path

NOTA = re.compile(r"<a:p><a:r>(<a:rPr[^>]*/>)<a:t>(.*?)</a:t></a:r>", re.S)


def separar(xml):
    def trocar(m):
        rpr = m.group(1).replace('lang="en-US"', 'lang="pt-BR"')
        linhas = [linha.rstrip("\r") for linha in m.group(2).split("\n")]
        corpo = "".join(f"<a:p><a:r>{rpr}<a:t>{linha}</a:t></a:r></a:p>" for linha in linhas[:-1])
        return corpo + f"<a:p><a:r>{rpr}<a:t>{linhas[-1]}</a:t></a:r>"
    return NOTA.sub(trocar, xml)


def main(caminho):
    caminho = Path(caminho)
    temporario = caminho.with_suffix(".tmp")
    alterados = 0
    with zipfile.ZipFile(caminho) as origem, zipfile.ZipFile(temporario, "w", zipfile.ZIP_DEFLATED) as destino:
        for item in origem.infolist():
            dados = origem.read(item.filename)
            if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", item.filename):
                novo = separar(dados.decode("utf-8"))
                if novo.encode("utf-8") != dados:
                    alterados += 1
                dados = novo.encode("utf-8")
            destino.writestr(item, dados)
    shutil.move(temporario, caminho)
    print(f"notas ajustadas em {alterados} slides")


if __name__ == "__main__":
    main(sys.argv[1])
