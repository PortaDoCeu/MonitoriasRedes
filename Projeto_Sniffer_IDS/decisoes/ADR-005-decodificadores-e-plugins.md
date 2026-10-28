# ADR-005: Decodificadores próprios atrás de uma interface de plugin

**Status:** Aceita

## Contexto

O sensor precisa entender Modbus TCP e S7comm agora, e outros protocolos industriais depois (DNP3, IEC 104, GOOSE, PROFINET). O decodificador é a parte do sensor que lê bytes vindos de qualquer equipamento da rede, inclusive de um atacante: é a principal superfície de ataque.

Existem bibliotecas em C e C++ para esses protocolos, mas em três grupos que não servem diretamente:

| Tipo | Exemplos | Por que não serve aqui |
|---|---|---|
| Pilhas de comunicação | libmodbus, snap7, p-net, lib60870, opendnp3 | Feitas para *participar* da conversa (cliente, servidor, dispositivo), não para observar os dois sentidos de uma conversa alheia |
| Ferramentas de análise e IDS | Wireshark (dissectors em C), Suricata, Zeek, nDPI | Rodam em Linux com centenas de MB; alocação dinâmica; grandes demais para o ESP32 |
| Pilha com assinante passivo | libiec61850 (assinante GOOSE) | A mais próxima do caso de uso; licença GPL ou comercial; vale estudar quando o GOOSE entrar |

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Decodificadores escritos à mão, atrás de uma interface `proto_t`** | Pequenos; memória fixa; cada campo de tamanho conferido; o núcleo não muda ao somar protocolos | Trabalho por protocolo; risco de interpretar errado (mitigado comparando com o Wireshark) |
| Adaptar trechos de dissectors do Wireshark | Lógica já testada | Licença GPL; código acoplado à infraestrutura do Wireshark |
| Decodificadores à mão, sem interface comum | Mais direto | Cada protocolo novo mexe no núcleo |

## Decisão

- Cada protocolo é um plugin `proto_t` com `name`, `tcp_port`, `frame_len()` e `decode()` (Arquitetura, seção 6.1).
- O plugin mantém estado por fluxo para casar pergunta e resposta.
- Todo campo de tamanho lido da rede é conferido contra o número de bytes realmente disponível antes de ser usado.
- Na versão Python, o registro de plugins é o dicionário `DECODIFICADORES = {502: ..., 102: ...}`.

## Justificativa

Num sensor passivo embarcado, um decodificador próprio é o caminho comum: cabe na memória, não traz dependências e pode ser escrito de forma defensiva. A interface de plugin isola esse trabalho: o núcleo continua igual quando um protocolo novo entra.

## Consequências

- Positivas: protocolo novo = um arquivo novo; decodificadores testáveis isoladamente.
- Negativas: protocolos complexos (GOOSE com codificação ASN.1/BER, PROFINET) exigem bem mais trabalho que Modbus e S7comm.

## Verificação

- Para cada plugin, um teste com mensagens truncadas e com campos de tamanho falsos (maiores que o pacote) termina sem leitura fora do buffer (no PC, compilado com AddressSanitizer).
- Para um `.pcap` da bancada, os campos decodificados batem com os do Wireshark (na versão Python, conferido com pyshark).

## Relacionadas

[ADR-004](ADR-004-evento-normalizado.md), [ADR-006](ADR-006-remontagem-tcp-limitada.md), [Arquitetura, seção 7](../Arquitetura.md#7-decodificação)
