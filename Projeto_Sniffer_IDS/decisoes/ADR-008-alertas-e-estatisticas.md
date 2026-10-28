# ADR-008: Alertas na hora e estatísticas por janela

**Status:** Aceita

## Contexto

Há dois consumidores com necessidades diferentes: a operação quer saber **na hora** que algo suspeito aconteceu; o modelo de séries temporais do TCC quer um **resumo regular** do comportamento. Mandar todo evento decodificado pelo Wi-Fi poderia estourar a banda e a fila de saída do ESP32.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Alertas imediatos + estatísticas por janela de 10 s** | Banda previsível; o TCC recebe séries regulares | Detalhe de cada evento normal se perde |
| Todo evento decodificado | Máximo de dados para pesquisa | Banda proporcional ao tráfego da planta; fila de saída enche sob carga |
| Só alertas | Mínimo tráfego | Nada para o modelo de comportamento |

## Decisão

- `ids/<sensor>/alert`: um alerta por mensagem, com o evento que o causou, QoS 1.
- `ids/<sensor>/stats`: a cada 10 s, contagens por (origem, destino, protocolo, operação, função), erros, bytes e os últimos valores, QoS 0.
- `ids/<sensor>/health`: a cada 30 s, contadores de descarte, memória mínima, tempo ligado e estado do SNTP.
- Fila de saída com prioridade: em falta de espaço, descarta estatísticas antes de alertas.
- Na versão Python: alertas na tela e em `alertas.csv`; janela impressa a cada 10 s; MQTT opcional.

## Justificativa

A janela fixa transforma o tráfego em séries temporais regulares, que é o formato que o detector do TCC consome. Os alertas não esperam a janela.

## Consequências

- Positivas: banda limitada e conhecida; o mesmo formato serve para painel e pesquisa.
- Negativas: para investigar um alerta em detalhe, é preciso uma captura completa em outro lugar; o sensor guarda só o evento do alerta.

## Verificação

- Com tráfego constante na bancada, chega exatamente uma mensagem em `stats` a cada 10 s (tolerância de 1 s).
- Com o broker desligado e tráfego suspeito, ao religar, o contador de alertas descartados é coerente com os alertas gerados.

## Relacionadas

[ADR-003](ADR-003-uplink-wifi-mqtt.md), [ADR-004](ADR-004-evento-normalizado.md), [Arquitetura, seção 10](../Arquitetura.md#10-saídas-no-mqtt)
