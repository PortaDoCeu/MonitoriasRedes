# ADR-019: Tecnologia do app

**Status:** Aceita

## Contexto

O app precisa rodar em qualquer celular da turma, sem instalação, sem internet, falar MQTT por WebSocket e desenhar um gráfico.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| App nativo (Android e iOS) | Experiência melhor | Instalação em celular pessoal; dois sistemas; fora do escopo |
| Framework (React, Vue) | Organização para apps grandes | Etapa de build; peso sem necessidade para uma tela |
| Bibliotecas via CDN | Nada a baixar | Quebra sem internet ([ADR-001](ADR-001-ambiente-e-requisitos.md)) |
| **HTML + JavaScript puro, bibliotecas servidas localmente** | Abre em qualquer navegador; sem build; funciona offline | Organização do código fica por conta de quem escreve |

## Decisão

- Um `index.html`, um `app.js` e um `estilo.css` em `middleware/static/`.
- **MQTT.js** (build para navegador) e **Chart.js**, baixados uma vez e guardados em `middleware/static/vendor/`, com a versão no nome do arquivo.
- Nenhuma requisição a domínio externo.
- Layout para tela de celular primeiro (largura a partir de 360 px).

## Justificativa

Uma tela com três valores, um gráfico e dois controles não precisa de framework. Guardar as bibliotecas no projeto é o que garante o requisito de funcionar sem internet.

## Consequências

- Positivas: qualquer aluno pode abrir o código da página e entender.
- Negativas: atualizar MQTT.js ou Chart.js é manual (baixar o arquivo novo).

## Verificação

- Com o notebook sem internet, abrir o app num celular: carrega completo.
- Aba Network do navegador: todas as requisições vão para `<ip-do-notebook>`.

## Relacionadas

[ADR-001](ADR-001-ambiente-e-requisitos.md), [ADR-014](ADR-014-autenticacao-e-acl.md), [ADR-020](ADR-020-interacao-de-comando.md), [ADR-028](ADR-028-versoes-fixadas.md)
