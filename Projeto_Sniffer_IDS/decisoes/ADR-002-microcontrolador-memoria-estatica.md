# ADR-002: ESP32 com FreeRTOS e memória estática

**Status:** Aceita com premissa (tamanhos e consumo de memória precisam ser medidos na placa)

## Contexto

O sensor deve ser barato, pequeno e instalável perto do switch, sem um computador inteiro. A placa de referência disponível é a LILYGO T-ETH-Lite (ESP32, 2 núcleos a 240 MHz, cerca de 520 KB de SRAM, Ethernet 100 Mbit, Wi-Fi), programada com ESP-IDF e FreeRTOS. Um sensor de segurança precisa funcionar meses sem reiniciar; fragmentação de memória e falta de memória em pico de tráfego são as falhas típicas de firmware de rede.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Microcontrolador, alocação só na partida** | Barato, baixo consumo; comportamento previsível sob carga | Pouca memória; limites fixos; mais trabalho de engenharia |
| Microcontrolador com `malloc` livre | Código mais simples | Fragmentação e falha por falta de memória em pico, difíceis de reproduzir |
| Linux embarcado (Raspberry Pi, gateway industrial) | Muita memória; pode usar bibliotecas prontas | Mais caro; sistema de arquivos e sistema operacional para manter e proteger; partida lenta |

## Decisão

- Alvo: **ESP32 com ESP-IDF e FreeRTOS**.
- **Nenhuma alocação dinâmica depois da partida.** Pool de quadros (32 × 1536 B), tabela de fluxos (32), estatísticas (256 entradas) e filas são criados no início, com tamanhos definidos em `cfg`.
- Quando um recurso enche, o sensor **descarta e conta** (ver Arquitetura, seção 9.3). Nunca bloqueia esperando memória.
- Núcleo portável em C99 (sem ESP-IDF) separado da camada de plataforma.

## Justificativa

Com memória fixa, o pior caso é conhecido na compilação: o sensor pode perder quadros, mas não trava. Separar o núcleo portável permite testar decodificadores e regras no PC, com `.pcap`, sem gravar a placa a cada mudança.

## Consequências

- Positivas: comportamento previsível; falhas visíveis nos contadores; núcleo testável no PC.
- Negativas: limites rígidos (fluxos, tamanho de mensagem); orçamento de memória apertado com Wi-Fi e TLS ligados.

## Verificação

- Busca no código do núcleo por `malloc`, `calloc`, `realloc` e `free` não encontra nenhuma chamada fora da inicialização.
- Na placa, sob carga máxima durante 1 hora, a menor memória livre publicada em `health` fica estável e acima de uma margem definida (a fixar depois da primeira medição).

## Relacionadas

[ADR-006](ADR-006-remontagem-tcp-limitada.md), [Arquitetura, seção 9](../Arquitetura.md#9-concorrência-memória-e-falhas)
