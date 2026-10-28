# ADR-006: Remontagem TCP limitada no C; nenhuma na aula

**Status:** Aceita

## Contexto

O TCP entrega um fluxo de bytes, não mensagens. Uma mensagem Modbus ou S7 pode chegar quebrada em dois segmentos, ou dois segmentos podem trazer duas mensagens juntas. Na bancada, com tráfego leve, quase sempre uma mensagem cabe num segmento; numa planta com muito tráfego, nem sempre. Remontar fluxos custa memória por conexão, que é o recurso mais escasso do ESP32.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Remontagem limitada: 32 fluxos, 1 KB por sentido** | Cobre as mensagens Modbus (até 260 B) e S7 do tamanho negociado pelos S7-1200 (PDU de 240 B, visto na bancada) | Mensagem maior que 1 KB ou segmentos fora de ordem demais são descartados |
| Sem remontagem (uma mensagem por segmento) | Muito simples | Perde mensagens quebradas; um atacante pode se esconder dividindo a mensagem |
| Remontagem completa | Não perde nada | Memória sem limite: inviável num microcontrolador |

## Decisão

- **No C:** tabela de 32 fluxos, buffer de 1 KB por sentido. O `frame_len()` do plugin diz onde termina cada mensagem. Segmento fora de ordem ou estouro do buffer: descarta o buffer daquele sentido, ressincroniza e conta em `reasm_overflow`.
- **Na aula (Python):** sem remontagem. Cada segmento é tratado como uma mensagem; o que não fechar com o tamanho declarado no cabeçalho é contado como "não decodificado". A remontagem é apresentada no fechamento como "o que falta para o projeto real".

## Justificativa

A remontagem limitada cobre o tráfego real de CLPs com memória previsível. Na aula, o tempo vai para os protocolos, e o `frame_len` já aparece como conceito (o tamanho que vem no cabeçalho) sem a tabela de fluxos.

## Consequências

- Positivas: o C resiste a mensagens divididas; a aula fica no tempo.
- Negativas: o Python da aula pode ser enganado por mensagens divididas de propósito, o que vira um exemplo de evasão no fechamento.

## Verificação

- Teste no PC: um `.pcap` com uma escrita Modbus dividida em dois segmentos gera exatamente um evento de escrita no C.
- O mesmo `.pcap` na versão Python gera um "não decodificado", demonstrando a limitação.

## Relacionadas

[ADR-002](ADR-002-microcontrolador-memoria-estatica.md), [ADR-005](ADR-005-decodificadores-e-plugins.md), [ADR-009](ADR-009-versao-de-aula-python.md)
