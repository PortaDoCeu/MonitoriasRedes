# Aula 3: o switch na rede da planta

Monitoria de Introdução às Redes de Comunicação, UFPE, 2026.2. Aula de 3 horas: 30 minutos de exposição e projeto em grupos no switch gerenciado do laboratório.

## Para a aula (raiz desta pasta)

| Arquivo | Uso |
|---|---|
| `slides_aula3.pptx` | apresentação com as falas nas notas do apresentador |
| `slides_aula3.pdf` | a mesma apresentação em PDF |
| `slides_aula3_notas.pdf` | roteiro de fala: miniatura de cada slide e o que dizer |
| `Aula.ipynb` | roteiro do projeto, para os alunos |
| `mapa_bancada.pdf` | **imprimir**: um para colar no switch e um por grupo |
| `ficha_comandos.pdf` | **imprimir**: uma por grupo |
| `guia_monitor.pdf` | guia completo do monitor: conceitos, gabarito, respostas, problemas |
| `gabarito_comandos.md` | todos os comandos do switch, com página do manual e como desfazer |
| `checklist_monitor.md` | o que testar no switch antes da aula |

## Outras pastas

| Pasta | Conteúdo |
|---|---|
| `referencias/` | manual oficial ExtremeXOS 21.1 e release notes |
| `fontes/` | fontes de tudo acima: `.tex`, scripts Python e do PowerPoint, figuras |
| `temporarios/` | arquivos gerados na compilação (`.aux`, `.log`, imagens do PPTX); pode apagar, fica fora do git |

## Para mudar o material

Edite o arquivo em `fontes/` e rode, nessa pasta:

```
.\compilar.ps1
```

Ele regera as figuras, o `Aula.ipynb`, todos os PDFs e o PowerPoint, colocando as entregas na raiz e os temporários em `temporarios/`. Feche o PowerPoint antes, senão o `.pptx` não pode ser substituído.
