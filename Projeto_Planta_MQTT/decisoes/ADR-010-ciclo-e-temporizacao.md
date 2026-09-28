# ADR-010: Ciclo de leitura e temporização

**Status:** Aceita

## Contexto

É preciso decidir de quanto em quanto tempo ler o CLP, em que ordem fazer leitura, heartbeat e comandos, e quanto esperar por uma resposta antes de desistir. Esses tempos definem o atraso percebido ([ADR-001](ADR-001-ambiente-e-requisitos.md)) e o watchdog do CLP ([ADR-005](ADR-005-seguranca-funcional-no-clp.md)).

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Ciclo de 100 ms | Tela mais fluida | 10 vezes mais mensagens e linhas no banco sem ganho visível para temperatura |
| **Ciclo de 1 s** | Atende os 2 s de telemetria; volume pequeno | Gráfico em degraus de 1 s |
| Heartbeat numa tarefa separada | Independe da leitura | Mais uma thread usando o Modbus, contra a [ADR-009](ADR-009-concorrencia-no-gateway.md) |

## Decisão

A cada 1 s, em ordem:
1. FC 3 lendo HR0 a HR9 (10 registradores, uma requisição).
2. FC 6 escrevendo o contador de heartbeat em HR12.
3. Publicação da telemetria e, se mudou, do status.
4. Até o próximo segundo: executar comandos da fila assim que chegarem.

Tempos:

| Parâmetro | Valor |
|---|---|
| Período de leitura | 1 s |
| Timeout de cada requisição Modbus | 0,5 s |
| Novas tentativas por requisição | 1 |
| Watchdog no CLP | 3 s sem mudança em HR12 |
| Espera por resposta no app | 3 s ([ADR-020](ADR-020-interacao-de-comando.md)) |

## Justificativa

Com timeout de 0,5 s e 1 nova tentativa, o pior caso de uma requisição é 1 s. Uma falha isolada custa no máximo um heartbeat; como o watchdog espera 3 s sem mudança, só uma falha que se repete por cerca de três ciclos seguidos leva o CLP ao estado seguro, o que é o comportamento desejado: o CLP para quando o gateway de fato perdeu o contato. O heartbeat no mesmo ciclo da leitura garante que ele só é enviado se o gateway estiver de fato funcionando.

## Consequências

- Positivas: 3 publicações de telemetria por segundo, cerca de 32 mil linhas por aula de 3 h, volume trivial para o SQLite.
- Negativas: o watchdog tem 3 s de reação, que é o tempo máximo de motor girando depois de o gateway morrer.

## Verificação

- Log do gateway mostra o período medido entre leituras: média 1,0 s, desvio inferior a 50 ms durante 10 min.
- Desligar o cabo do CLP por 1 s não aciona o watchdog; por 4 s aciona.

## Relacionadas

[ADR-001](ADR-001-ambiente-e-requisitos.md), [ADR-005](ADR-005-seguranca-funcional-no-clp.md), [ADR-009](ADR-009-concorrencia-no-gateway.md), [ADR-017](ADR-017-banco-de-dados.md)
