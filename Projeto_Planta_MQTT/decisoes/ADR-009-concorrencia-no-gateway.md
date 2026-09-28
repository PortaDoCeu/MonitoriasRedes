# ADR-009: Modelo de concorrência do gateway

**Status:** Aceita

## Contexto

Comandos chegam pela thread de rede do paho-mqtt a qualquer momento, enquanto o laço principal lê o CLP a cada segundo. Se as duas threads usarem o cliente Modbus ao mesmo tempo, as requisições se misturam na mesma conexão TCP e as respostas podem ser atribuídas à requisição errada.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Escrever no CLP direto no callback do MQTT | Menor latência | Acesso concorrente ao mesmo socket Modbus |
| Lock em volta de cada chamada Modbus | Seguro | Callback do MQTT fica bloqueado esperando o CLP; lógica espalhada |
| **Fila de comandos; só o laço principal usa o Modbus** | Um dono só da conexão; callback do MQTT nunca bloqueia | Latência de até um ciclo, resolvida esperando na fila ([ADR-010](ADR-010-ciclo-e-temporizacao.md)) |

## Decisão

- O laço principal é o único dono do `ModbusTcpClient`.
- O callback `on_message` do MQTT só faz o parse do JSON e coloca o comando numa `queue.Queue`.
- O laço principal espera na fila com `get(timeout=...)` até o próximo instante de leitura, então comandos são executados assim que chegam, sem esperar o ciclo seguinte.
- Publicações MQTT podem sair de qualquer thread (o paho-mqtt é seguro para isso).

## Justificativa

É o padrão produtor e consumidor: uma fila entre quem recebe e quem executa. Elimina a condição de corrida por construção, em vez de tentar controlá-la com locks.

## Consequências

- Positivas: não existe caminho no código em que duas requisições Modbus saiam ao mesmo tempo.
- Negativas: se o CLP travar numa requisição, os comandos esperam na fila até o timeout ([ADR-010](ADR-010-ciclo-e-temporizacao.md)).

## Verificação

- Revisão: o objeto do cliente Modbus só é referenciado dentro do laço principal.
- Teste: enviar 50 comandos em rajada com o simulado; todos recebem resposta, na ordem, e nenhuma leitura falha.

## Relacionadas

[ADR-008](ADR-008-stack-do-gateway.md), [ADR-010](ADR-010-ciclo-e-temporizacao.md), [ADR-011](ADR-011-validacao-de-comandos.md)
