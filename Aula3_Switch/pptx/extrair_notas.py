r"""Extrai o \note{} de cada slide de slides_projeto.tex e converte para texto simples.

Uso (na pasta aula/pptx):
    python extrair_notas.py ../slides_projeto.tex notas.json
"""

import json
import re
import sys
from pathlib import Path

BS = "\\"


def blocos_note(texto):
    r"""Conteúdo de cada \note{...} depois de \begin{document}, respeitando chaves aninhadas."""
    abertura = BS + "note{"
    notas, i = [], texto.index(BS + "begin{document}")
    while (i := texto.find(abertura, i)) != -1:
        j = i + len(abertura)
        nivel = 1
        while nivel:
            if texto[j] == BS:
                j += 2
                continue
            nivel += {"{": 1, "}": -1}.get(texto[j], 0)
            j += 1
        notas.append(texto[i + len(abertura):j - 1])
        i = j
    return notas


SUBSTITUICOES = [
    (r"\\textbackslash\s?", r"\\"),
    (r"\$\\times\$", "×"), (r"\$\\neq\$", "≠"), (r"\\times", "×"),
    (r"\{,\}", ","), (r"\$", ""),
    (r"``", "\u201c"), (r"''", "\u201d"),
    (r"\\_", "_"), (r"\\#", "#"), (r"\\&", "&"),
]


def para_texto(latex):
    t = latex.replace("%\n", "\n")
    # chaves escapadas viram marcadores antes de remover os comandos de formatação
    t = t.replace(BS + "{", "\x01").replace(BS + "}", "\x02")
    t = re.sub(r"\\tempo\{([^}]*)\}", r"[\1]", t)
    t = re.sub(r"\\pergunta\{", "PERGUNTE: {", t)
    t = re.sub(r"\\begin\{itemize\}|\\end\{itemize\}", "", t)
    t = re.sub(r"\\item\s*", "\n- ", t)
    for padrao, troca in SUBSTITUICOES:
        t = re.sub(padrao, troca, t)
    for _ in range(3):
        t = re.sub(r"\\(texttt|textbf|emph|textit)\{([^{}]*)\}", r"\2", t)
    t = t.replace("{", "").replace("}", "").replace("\x01", "{").replace("\x02", "}")
    linhas = [re.sub(r"[ \t]+", " ", linha).strip() for linha in t.splitlines()]
    return "\n".join(linha for linha in linhas if linha)


if __name__ == "__main__":
    origem, destino = Path(sys.argv[1]), Path(sys.argv[2])
    notas = [para_texto(n) for n in blocos_note(origem.read_text(encoding="utf-8"))]
    destino.write_text(json.dumps(notas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(notas)} notas extraídas")
    for numero, nota in enumerate(notas, 1):
        if re.search(r"\\[a-zA-Z]{2,}\b", nota.replace(BS + "Scripts", "").replace(BS + "parar", "")):
            print(f"ATENÇÃO slide {numero}: sobrou comando LaTeX:\n{nota}\n")
