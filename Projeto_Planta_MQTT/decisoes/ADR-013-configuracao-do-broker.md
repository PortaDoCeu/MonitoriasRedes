# ADR-013: Configuração do broker

**Status:** Aceita

## Contexto

O broker é o conduto entre a zona OT e a zona TI. Ele recebe conexões de programas locais (gateway e middleware) e dos celulares, que só conseguem falar MQTT por WebSocket a partir do navegador.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Broker público na internet | Nada a instalar | Viola o requisito sem internet e expõe a planta |
| Broker embutido em Python (por exemplo amqtt) | Um só ecossistema | Menos maduro; mais código para manter |
| EMQX ou HiveMQ | Muitos recursos | Pesados para um notebook; recursos sem uso |
| **Mosquitto 2.x** | Leve, padrão de fato, instalador para Windows, suporta WebSocket | Configuração em arquivo de texto |

## Decisão

Mosquitto 2.x com esta configuração (`broker/mosquitto.conf`):

```
per_listener_settings false
allow_anonymous false
password_file broker/senhas
acl_file broker/acl
persistence false

listener 1883 127.0.0.1

listener 9001
protocol websockets
```

- A porta 1883 só aceita conexões do próprio notebook (gateway e middleware).
- A porta 9001 (WebSocket) aceita conexões da rede, para os celulares.
- Sem persistência: ao reiniciar, o broker começa vazio e o gateway republica o que é retido ([ADR-012](ADR-012-reconexao.md)).

## Justificativa

Nenhum programa de fora do notebook precisa de MQTT puro, então a porta 1883 nem é exposta. Sem persistência, nenhum estado velho sobrevive a um reinício do broker, o que elimina uma classe de defeitos (status antigo aparecendo como atual).

## Consequências

- Positivas: superfície exposta na rede reduzida a uma porta MQTT.
- Negativas: a porta 9001 carrega MQTT sem criptografia ([ADR-015](ADR-015-sem-tls-na-monitoria.md)).

## Verificação

- De outra máquina na rede, conectar em `<ip-do-notebook>:1883`: conexão recusada.
- Conectar sem usuário em `:9001`: recusado.
- Reiniciar o Mosquitto e conferir que `bancada1/gateway/estado` volta retido em até 30 s.

## Relacionadas

[ADR-012](ADR-012-reconexao.md), [ADR-014](ADR-014-autenticacao-e-acl.md), [ADR-015](ADR-015-sem-tls-na-monitoria.md), [ADR-022](ADR-022-firewall-do-notebook.md), [ADR-024](ADR-024-execucao-dos-servicos.md)
