# ADR-009: Versão de aula em Python idiomático, 4 arquivos, Scapy

**Status:** Aceita

## Contexto

A monitoria tem 3 horas, a turma tem Python básico e o objetivo é escrever o sensor inteiro em sala, com o monitor digitando no projetor. A aula também é a introdução ao TCC e ao projeto de pesquisa, então precisa mostrar o caminho até o sensor real em C.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Python idiomático em 4 arquivos, com o equivalente em C mostrado em cada etapa** | Cabe em 3 h (~240 linhas); fácil de acompanhar | Não imita a estrutura de memória do C |
| Python espelhando os 15 módulos do C | Correspondência um para um | Arquivos demais; a turma se perde navegando |
| Escrever em C direto | É o projeto real | Inviável em 3 h para uma turma com Python básico |

Bibliotecas de captura avaliadas: **Scapy** (captura e lê `.pcap`, mantida, padrão em segurança), **dpkt** (rápida, mas sem captura ao vivo e sem versão nova desde 2022), **pyshark** (decodifica S7comm, mas esconde os bytes e depende do tshark), **pcapy-ng** (só captura).

## Decisão

- 4 arquivos: `captura.py`, `protocolos.py`, `regras.py`, `sensor.py` (Arquitetura, seção 14).
- **Scapy** só em `captura.py`, para capturar e separar Ethernet/IP/TCP.
- **Modbus e S7comm decodificados à mão com `struct`**, como no C.
- Cada PC gera o próprio tráfego com um CLP da bancada; nenhuma dependência da porta espelho.
- Cada etapa termina num ponto de checagem com o arquivo pronto, para quem se perder.
- pyshark fica fora da aula, só nos testes do monitor, para conferir os decodificadores contra o Wireshark.

## Justificativa

A divisão em 4 arquivos segue as 4 grandes responsabilidades do sensor (capturar, decodificar, detectar, orquestrar), que são as mesmas do C. A turma aprende os bytes dos protocolos, que é a parte que muda menos entre Python e C, e vê no fim por que o Python não basta.

## Consequências

- Positivas: o sensor inteiro cabe na aula; o mapa para o C fica explícito.
- Negativas: captura ao vivo no Windows exige Npcap e terminal como administrador; o desempenho do Python limita o teste de carga (o que é usado como conteúdo).

## Verificação

- O código completo, rodando sobre o `.pcap` de reserva, gera os mesmos eventos que o Wireshark mostra para os mesmos pacotes.
- O código de cada ponto de checagem roda sozinho.
- Ensaio cronometrado da aula fica dentro de 3 h.

## Relacionadas

[ADR-005](ADR-005-decodificadores-e-plugins.md), [ADR-006](ADR-006-remontagem-tcp-limitada.md), [Arquitetura, Parte B](../Arquitetura.md#parte-b-a-versão-de-aula-em-python)
