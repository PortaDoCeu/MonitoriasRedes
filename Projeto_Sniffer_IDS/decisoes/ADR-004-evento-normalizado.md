# ADR-004: Evento normalizado com operação genérica e amostra de valores

**Status:** Aceita

## Contexto

Regras, estatísticas e saída precisam funcionar para qualquer protocolo. Se cada módulo conhecer o formato do Modbus e do S7comm, somar um protocolo novo obriga a mexer em todos. Ao mesmo tempo, o modelo de séries temporais do TCC precisa dos valores trocados (registradores lidos, setpoints escritos), não só da contagem de pacotes.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Um evento único com `op` genérica (leitura, escrita, controle, diagnóstico, outra) e até 4 valores** | Regras valem para todos os protocolos; o TCC recebe valores | Detalhes específicos do protocolo ficam de fora; os valores tornam o sensor um coletor de dados de processo |
| Um tipo de evento por protocolo | Nada se perde | Regras e estatísticas duplicadas para cada protocolo |
| Evento sem valores | Menos dado sensível; menor | Inútil para detecção baseada no comportamento físico da planta |

## Decisão

- Todo plugin produz o mesmo `event_t` (Arquitetura, seção 6.2), com `op` genérica, endereço, quantidade, `status` e **até 4 valores**.
- O código bruto do protocolo fica em `func`, para quem precisar do detalhe.
- Na versão Python, o mesmo conteúdo vira a dataclass `Evento`.

## Justificativa

A operação genérica é o que permite escrever "escrita vinda de quem não é engenharia" uma vez só. Os valores são o elo entre o sensor de rede e o detector de comportamento físico do TCC, que precisa saber o que foi lido e escrito, não só quem falou com quem.

## Consequências

- Positivas: protocolo novo só exige um plugin; o TCC recebe séries de valores reais.
- Negativas: os valores são dados de processo da planta, portanto sensíveis. O canal de saída precisa de TLS ([ADR-003](ADR-003-uplink-wifi-mqtt.md)), e capturas da bancada precisam ser anonimizadas antes de virar material público. 4 valores por evento é uma amostra, não o conteúdo inteiro de uma leitura grande.

## Verificação

- Busca no código de `rules` e `stats` não encontra nenhuma referência a Modbus, S7 ou códigos de função específicos.
- Para uma leitura Modbus da bancada, o valor em `vals[0]` é igual ao mostrado pelo Wireshark para o mesmo pacote.

## Relacionadas

[ADR-005](ADR-005-decodificadores-e-plugins.md), [ADR-008](ADR-008-alertas-e-estatisticas.md)
