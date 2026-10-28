# ADR-003: Uplink por Wi-Fi e MQTT com TLS (risco aceito)

**Status:** Aceita

## Contexto

Como a Ethernet monitorada só escuta ([ADR-001](ADR-001-sensor-passivo.md)), o sensor precisa de outro caminho para entregar alertas e estatísticas. A placa de referência tem uma porta Ethernet e Wi-Fi. Os consumidores (painel e modelo de IA do TCC) ficam na rede de gestão.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Wi-Fi + MQTT** | Já existe na placa; sem cabo extra | Wi-Fi em planta é mal visto: interferência, alcance, mais uma porta de entrada sem fio |
| Segunda Ethernet (módulo SPI, como W5500) | Isolamento físico; mais confiável | Hardware extra; mais um driver |
| Mesma Ethernet para escutar e publicar | Nenhum hardware extra | Deixa de ser passivo; o sensor passa a ter IP na rede da planta |
| HTTP/REST em vez de MQTT | Simples | Cada mensagem abre conexão; sem publicação para vários consumidores |

## Decisão

- Saída por **Wi-Fi**, com **MQTT sobre TLS** (porta 8883) e autenticação por certificado de cliente.
- Credenciais e certificado ficam na NVS cifrada, nunca no código.
- O sensor só **publica**. Não assina nenhum tópico de comando ou configuração ([ADR-007](ADR-007-regras-compiladas.md)).
- Evolução prevista: segunda Ethernet para a rede de gestão.

## Justificativa

Para o protótipo e para a pesquisa, o Wi-Fi resolve sem hardware extra e mantém a Ethernet monitorada sem IP. O risco do Wi-Fi é reduzido porque o sensor não aceita nada pela rede sem fio: só publica, com TLS.

## Consequências

- Positivas: protótipo com uma placa só; consumidores podem ser somados sem mudar o sensor.
- Negativas: a entrega depende do Wi-Fi; o sensor tem uma interface sem fio que precisa ser protegida. Quando o broker fica fora do ar, estatísticas e depois alertas são descartados e contados.

## Verificação

- Uma captura do tráfego Wi-Fi do sensor mostra apenas TLS na porta 8883 (e SNTP e DNS, se usados), nenhum MQTT em texto claro.
- Uma mensagem publicada por outro cliente no tópico `ids/<sensor>/#` não altera nada no comportamento do sensor.

## Relacionadas

[ADR-001](ADR-001-sensor-passivo.md), [ADR-008](ADR-008-alertas-e-estatisticas.md)
