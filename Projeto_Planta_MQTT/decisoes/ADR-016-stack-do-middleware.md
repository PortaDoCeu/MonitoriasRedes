# ADR-016: Linguagem e bibliotecas do middleware

**Status:** Aceita

## Contexto

O middleware assina todos os tópicos, grava no banco e atende HTTP (página do app, histórico, exportação). São duas fontes de eventos: mensagens MQTT e requisições HTTP.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Flask | Muito simples | Sem validação de parâmetros nem documentação automática |
| **FastAPI + uvicorn** | Valida parâmetros das rotas; gera página de documentação em `/docs`, útil em aula | Um conceito a mais (async) no código das rotas |
| Servidor HTTP da biblioteca padrão | Nada a instalar | Muito código manual para rotas e JSON |

## Decisão

- **FastAPI** servido por **uvicorn**, rotas síncronas (`def`, não `async def`) para manter o código linear.
- **paho-mqtt** 2.x com `loop_start()`, iniciado no evento de inicialização do FastAPI.
- **sqlite3** da biblioteca padrão.
- Um único escritor no banco: só a thread do MQTT faz `INSERT`. As rotas HTTP abrem conexões próprias só para leitura.

## Justificativa

O FastAPI entrega validação e a página `/docs` sem esforço, e `/docs` permite mostrar a API funcionando em aula. Com um único escritor, não há disputa de escrita no SQLite.

## Consequências

- Positivas: o mesmo paho-mqtt do gateway; a turma vê um só cliente MQTT nos dois programas.
- Negativas: FastAPI e uvicorn são dependências a mais que o gateway não tem.

## Verificação

- `GET /docs` abre a documentação com as três rotas.
- Teste de carga simples: 40 requisições simultâneas a `/historico` enquanto a telemetria é gravada; nenhuma falha de "database is locked".

## Relacionadas

[ADR-008](ADR-008-stack-do-gateway.md), [ADR-017](ADR-017-banco-de-dados.md), [ADR-018](ADR-018-api-http.md)
