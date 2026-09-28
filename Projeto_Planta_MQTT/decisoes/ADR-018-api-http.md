# ADR-018: API HTTP do middleware

**Status:** Aceita

## Contexto

O app precisa do histórico para o gráfico e a aula precisa terminar com um entregável reproduzível: os dados coletados, num formato que qualquer aluno abra.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| App lê o SQLite diretamente | Nenhuma API | Impossível a partir do navegador |
| Histórico também por MQTT (pedido e resposta) | Um protocolo só | MQTT não é feito para consulta; complica o app |
| **API HTTP somente leitura** | Padrão para consultas; CSV abre em qualquer planilha | Uma porta a mais (8000) |

## Decisão

| Rota | Parâmetros | Retorno |
|---|---|---|
| `GET /` | | Página do app |
| `GET /historico` | `grandeza` (temperatura, velocidade, referencia), `horas` (1 a 3) | JSON com lista de `{ts, valor, unidade}` |
| `GET /comandos` | `limite` (1 a 200, padrão 50) | JSON com os últimos comandos e resultados |
| `GET /exportar.csv` | | CSV com todas as medições, separador `;`, decimal com vírgula |
| `GET /docs` | | Documentação automática do FastAPI |

- Somente leitura: nenhuma rota altera dados ou comanda a planta. Comandos só existem por MQTT.
- Sem autenticação: os dados são os mesmos que a turma já vê ao vivo.
- Página e API na mesma origem, portanto sem CORS.

## Justificativa

Deixar o comando fora do HTTP mantém um único caminho de comando (MQTT com ACL), em vez de dois caminhos com regras diferentes. O CSV com `;` e vírgula decimal abre direto no Excel configurado em português.

## Consequências

- Positivas: o entregável da aula é um clique.
- Negativas: sem paginação no CSV; aceitável pelo volume estimado na [ADR-017](ADR-017-banco-de-dados.md).

## Verificação

- `GET /historico?grandeza=pressao` retorna 422.
- `GET /exportar.csv` abre no Excel com colunas separadas e números corretos.
- Nenhuma rota aceita POST, PUT ou DELETE (405).

## Relacionadas

[ADR-001](ADR-001-ambiente-e-requisitos.md), [ADR-014](ADR-014-autenticacao-e-acl.md), [ADR-016](ADR-016-stack-do-middleware.md), [ADR-017](ADR-017-banco-de-dados.md)
