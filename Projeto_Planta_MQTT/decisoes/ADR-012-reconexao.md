# ADR-012: Reconexão e recuperação do gateway

**Status:** Aceita

## Contexto

Durante a aula, o cabo do CLP pode ser desconectado, o CLP pode ir para STOP, o broker pode ser reiniciado. O gateway não pode terminar com erro nem exigir que alguém o reinicie.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Encerrar e depender de um supervisor externo para reiniciar | Código mais simples | Exige supervisor; perde o estado; no Windows não há um padrão simples |
| Tentar reconectar em laço sem espera | Reconecta rápido | Inunda a rede e o log quando o CLP some por minutos |
| **Reconectar com intervalo fixo (Modbus) e com recuo (MQTT)** | Recupera sozinho; carga controlada | Até 5 s para perceber o CLP de volta |

## Decisão

- Modbus: se uma leitura falhar duas vezes seguidas, fecha a conexão, publica status com o CLP indisponível e tenta reconectar a cada 5 s.
- MQTT: reconexão automática do paho-mqtt com recuo de 1 a 30 s (`reconnect_delay_set(1, 30)`).
- Ao (re)conectar no broker, o gateway publica `gateway/estado = online` e o último status conhecido, ambos retidos, porque o broker não tem persistência ([ADR-013](ADR-013-configuracao-do-broker.md)).
- Enquanto o broker estiver fora, o gateway continua lendo o CLP e escrevendo o heartbeat. A planta não depende do broker.
- Comandos na fila há mais de 3 s são descartados com resposta `falhou` e motivo `expirado`, para que um comando antigo nunca seja executado depois de uma reconexão.

## Justificativa

O descarte de comando expirado é a contrapartida, no gateway, da regra de nunca reter comandos no broker ([ADR-006](ADR-006-contrato-de-dados.md)): nenhum comando velho pode agir sobre a planta.

## Consequências

- Positivas: o sistema se recupera de qualquer queda sem intervenção.
- Negativas: com o broker fora, o app não recebe nada, mas a planta segue segura pelo heartbeat.

## Verificação

- Tirar o cabo do CLP por 30 s e recolocar: dados voltam em até 6 s, sem reiniciar nada.
- Reiniciar o serviço do Mosquitto: app volta a mostrar dados em até 30 s e mostra o status retido correto.
- Enfileirar um comando com o CLP desconectado, reconectar após 10 s: o comando não é executado e a resposta é `falhou` com `expirado`.

## Relacionadas

[ADR-006](ADR-006-contrato-de-dados.md), [ADR-009](ADR-009-concorrencia-no-gateway.md), [ADR-013](ADR-013-configuracao-do-broker.md), [Arquitetura.md, seção 7](../Arquitetura.md)
