# ADR-017: Banco de dados

**Status:** Aceita

## Contexto

É preciso guardar o histórico de medições e o log de comandos de uma aula, consultar por intervalo de tempo para o gráfico e exportar ao final.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| InfluxDB | Feito para séries temporais | Um servidor a mais para instalar e manter |
| PostgreSQL | Robusto | Servidor, usuário e senha a mais; exagero para o volume |
| **SQLite** | Um arquivo; já vem com o Python; fácil de entregar à turma | Um escritor por vez |

## Decisão

- SQLite, arquivo `dados/planta.db`, criado pelo middleware na primeira execução.
- `PRAGMA journal_mode=WAL` para permitir leituras enquanto a thread do MQTT escreve.
- Esquema da [seção 8 do Arquitetura.md](../Arquitetura.md), mais o índice:

```sql
CREATE INDEX IF NOT EXISTS idx_medicoes_grandeza_ts ON medicoes (grandeza, ts);
```

- `ts` em texto UTC ISO 8601, o mesmo valor que veio no JSON do gateway.
- Sem expurgo automático. Estimativa: 3 grandezas por segundo durante 3 h dão cerca de 32 mil linhas por aula, poucos megabytes.
- Um arquivo por semestre; ao iniciar um novo período, o arquivo antigo é arquivado.

## Justificativa

O volume de uma aula não justifica um servidor de banco. Texto ISO 8601 em UTC ordena corretamente como texto e evita qualquer ambiguidade de fuso.

## Consequências

- Positivas: o banco inteiro pode ser copiado como um arquivo.
- Negativas: consultas por horário local precisam converter de UTC na exibição (feito no app).

## Verificação

- `PRAGMA journal_mode;` retorna `wal`.
- `EXPLAIN QUERY PLAN` da consulta de histórico usa o índice `idx_medicoes_grandeza_ts`.
- Após o ensaio de 3 h, o arquivo tem menos de 20 MB.

## Relacionadas

[ADR-010](ADR-010-ciclo-e-temporizacao.md), [ADR-016](ADR-016-stack-do-middleware.md), [ADR-018](ADR-018-api-http.md), [ADR-023](ADR-023-relogio.md)
