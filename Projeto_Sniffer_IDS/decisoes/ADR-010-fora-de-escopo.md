# ADR-010: Fora de escopo: S7comm-plus, tráfego com TLS, fragmentação IP e IPv6

**Status:** Aceita

## Contexto

Nem todo tráfego da rede da planta pode ou deve ser decodificado pela primeira versão. É preciso dizer claramente o que o sensor não vê, para que ninguém confie nele além do que ele entrega.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Declarar fora de escopo, mas identificar e contar** | Escopo realista; o sensor ainda mostra que esse tráfego existe | Ataques por esses canais não são detectados pelo conteúdo |
| Tentar decodificar tudo | Cobertura maior | Inviável em memória e tempo; protocolos protegidos não podem ser lidos por um observador passivo |

## Decisão

| Fora de escopo | Motivo | O que o sensor faz |
|---|---|---|
| **S7comm-plus** (TIA Portal online; S7-1200/1500 com acesso otimizado) | Protocolo diferente (protocol ID `0x72`), com proteção de integridade; nas versões novas, dentro de TLS | Reconhece pelo ID e conta por par de IPs |
| Tráfego com TLS (OPC UA seguro, Modbus/TCP Security, HTTPS) | Cifrado | Conta por par de IPs e porta |
| Fragmentação IP | Rara em rede de CLP | Conta como "não decodificado" |
| IPv6 | Ausente na bancada e raro em plantas atuais | Conta como "não decodificado" |

O S7comm "clássico" (protocol ID `0x32`), usado pelo PUT/GET entre CLPs, continua no escopo.

## Justificativa

A tendência em OT é proteger os protocolos com integridade e criptografia. Isso é bom para a planta e limita qualquer sensor passivo à análise de metadados (quem fala com quem, quando e quanto). Deixar isso explícito é parte de um sensor honesto.

## Consequências

- Positivas: escopo cabível no ESP32 e na aula.
- Negativas: uma estação de engenharia mal-intencionada usando o TIA Portal (S7comm-plus) não tem o conteúdo inspecionado. O que aparece é a conversa em si, que já pode ser uma regra (estação desconhecida falando S7comm-plus com um CLP).

## Verificação

- Um `.pcap` com o TIA Portal online gera contagem de S7comm-plus em `stats` e nenhum evento S7comm decodificado.

## Relacionadas

[ADR-005](ADR-005-decodificadores-e-plugins.md), [Arquitetura, seção 11](../Arquitetura.md#11-limitações-declaradas)
