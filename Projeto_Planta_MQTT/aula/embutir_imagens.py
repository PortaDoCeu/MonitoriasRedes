"""Embute no notebook as imagens referenciadas por caminho, como anexos das células.

Troca ![texto](../img/x.png) por ![texto](attachment:x.png) e grava o PNG
dentro do próprio .ipynb. Assim a imagem aparece em qualquer lugar (VS Code,
Jupyter, GitHub, pacote dos alunos), sem depender de pastas fora do notebook,
que o VS Code bloqueia.

Uso (na pasta Projeto_Planta_MQTT):
    python aula/embutir_imagens.py aula/Aula.ipynb
"""

import base64
import json
import re
import sys
from pathlib import Path

IMAGEM = re.compile(r"!\[([^\]]*)\]\((?!attachment:)([^)]+\.png)\)")


def main(caminho):
    caminho = Path(caminho)
    nb = json.loads(caminho.read_text(encoding="utf-8"))
    total = 0
    for celula in nb["cells"]:
        if celula["cell_type"] != "markdown":
            continue
        texto = "".join(celula["source"])
        anexos = celula.get("attachments", {})

        def trocar(m):
            nonlocal total
            arquivo = (caminho.parent / m.group(2)).resolve()
            if not arquivo.exists():
                raise FileNotFoundError(f"imagem não encontrada: {arquivo}")
            anexos[arquivo.name] = {"image/png": base64.b64encode(arquivo.read_bytes()).decode("ascii")}
            total += 1
            return f"![{m.group(1)}](attachment:{arquivo.name})"

        novo = IMAGEM.sub(trocar, texto)
        if novo != texto:
            celula["source"] = novo.splitlines(keepends=True)
            celula["attachments"] = anexos
    caminho.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{total} imagens embutidas em {caminho}")


if __name__ == "__main__":
    main(sys.argv[1])
