# ADR-001: Sensor passivo, sem IP na rede da planta

**Status:** Aceita

## Contexto

Na rede de uma planta, a disponibilidade vem antes de tudo: um equipamento novo não pode atrasar, alterar nem derrubar a comunicação entre CLPs, IHMs e SCADA. O sensor também é um alvo: ele lê tudo o que passa, então quem o controlar ganha uma posição privilegiada na rede.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Passivo, porta espelho (SPAN) ou TAP, sem IP** | Não interfere no processo; invisível na rede monitorada; se falhar, nada muda na planta | Não bloqueia ataques, só avisa; depende de o switch espelhar bem |
| Em linha (o tráfego atravessa o sensor, que pode bloquear) | Pode impedir um ataque | Se o sensor travar, a planta para; latência extra; um falso positivo derruba comunicação legítima |
| Sensor com IP na rede da planta, consultando os equipamentos | Mais informação (pergunta direto ao CLP) | Gera tráfego e carga nos CLPs; exposto a ataques pela própria rede monitorada |

## Decisão

- A interface Ethernet monitorada fica em **modo promíscuo e sem pilha IP**: sem endereço, sem ARP, sem DHCP.
- **Nenhum módulo tem caminho de transmissão** por essa interface.
- A ligação com a planta é por porta espelho do switch; em instalação definitiva, preferir TAP passivo.
- Toda comunicação de saída do sensor vai por outra interface ([ADR-003](ADR-003-uplink-wifi-mqtt.md)).

## Justificativa

Em OT, um sensor que pode causar parada não é aceito pela operação. O modo passivo troca a capacidade de bloquear pela garantia de não interferir, que é o padrão dos sistemas de detecção para redes industriais.

## Consequências

- Positivas: falha ou ataque ao sensor não afeta o processo; o sensor não aparece em varreduras da rede da planta.
- Negativas: o sensor só detecta e avisa. A porta espelho pode perder quadros sob carga e não copia quadros com erro de camada 1; o TAP resolve, mas custa um equipamento a mais.

## Verificação

- Com o sensor ligado na porta espelho, uma captura feita em outra porta do switch, durante 10 minutos, não mostra **nenhum** quadro com o MAC de origem do sensor.
- Uma varredura (ping e ARP) na faixa da planta não encontra o sensor.

## Relacionadas

[ADR-003](ADR-003-uplink-wifi-mqtt.md), [Arquitetura, seção 2](../Arquitetura.md#2-onde-o-sensor-fica)
