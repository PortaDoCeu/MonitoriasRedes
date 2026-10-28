# Decisões de Projeto (ADRs)

Registro das decisões do sensor passivo de tráfego industrial. A arquitetura em si está em [Arquitetura.md](../Arquitetura.md).

Cada arquivo é uma ADR (*Architecture Decision Record*): uma decisão, por que ela foi tomada, o que se abriu mão e como verificar que ela está sendo cumprida.

## Como ler

| Seção | Conteúdo |
|---|---|
| Status | `Aceita` ou `Aceita com premissa` (depende de algo ainda não conferido na placa) |
| Contexto | O problema e as restrições |
| Alternativas consideradas | Opções avaliadas, com prós e contras |
| Decisão | O que foi escolhido |
| Justificativa | Por que essa e não as outras |
| Consequências | O que se ganha e o que se perde |
| Verificação | Teste objetivo que prova que a decisão está sendo cumprida |

Uma ADR aceita não é editada para mudar de ideia. Se a decisão mudar, cria-se uma ADR nova que a substitui, e a antiga recebe no status "Substituída por ADR-0XX".

## Índice

| ADR | Decisão | Parte | Status |
|---|---|---|---|
| [001](ADR-001-sensor-passivo.md) | Sensor passivo: Ethernet sem IP, nunca transmite na rede da planta | C | Aceita |
| [002](ADR-002-microcontrolador-memoria-estatica.md) | ESP32 com FreeRTOS; memória estática, descarta e conta | C | Aceita com premissa |
| [003](ADR-003-uplink-wifi-mqtt.md) | Uplink por Wi-Fi e MQTT com TLS (risco aceito) | C | Aceita |
| [004](ADR-004-evento-normalizado.md) | Evento normalizado com operação genérica e amostra de valores | C e Python | Aceita |
| [005](ADR-005-decodificadores-e-plugins.md) | Decodificadores próprios atrás de uma interface de plugin | C e Python | Aceita |
| [006](ADR-006-remontagem-tcp-limitada.md) | Remontagem TCP limitada no C; nenhuma na aula | C e Python | Aceita |
| [007](ADR-007-regras-compiladas.md) | Regras compiladas no firmware | C | Aceita |
| [008](ADR-008-alertas-e-estatisticas.md) | Saída: alertas na hora e estatísticas por janela | C e Python | Aceita |
| [009](ADR-009-versao-de-aula-python.md) | Versão de aula em Python idiomático, 4 arquivos, Scapy | Python | Aceita |
| [010](ADR-010-fora-de-escopo.md) | Fora de escopo: S7comm-plus, tráfego com TLS, fragmentação IP, IPv6 | C e Python | Aceita |
