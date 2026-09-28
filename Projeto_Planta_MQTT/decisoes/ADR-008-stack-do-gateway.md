# ADR-008: Linguagem e bibliotecas do gateway

**Status:** Aceita

## Contexto

O gateway precisa falar Modbus TCP como cliente e MQTT como cliente, nos dois sentidos, num notebook com Windows 11. A decisão de usar Python já foi tomada por Gabriel; falta fixar as bibliotecas e o modo de uso.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| pymodbus assíncrono (asyncio) + cliente MQTT assíncrono | Um só modelo de concorrência | asyncio é pesado para a turma ler; mais difícil de depurar ao vivo |
| **pymodbus síncrono + paho-mqtt com thread de rede própria** | Código linear, fácil de explicar; duas bibliotecas maduras e muito usadas | Duas threads (principal e rede MQTT) a coordenar |
| minimalmodbus / pyModbusTCP | Simples | pyModbusTCP é menos usado e mais limitado; minimalmodbus é só serial |

## Decisão

- Python 3.12 (a versão já instalada no notebook).
- **pymodbus** 3.x, cliente síncrono `ModbusTcpClient`.
- **paho-mqtt** 2.x, com `CallbackAPIVersion.VERSION2` e `loop_start()` (thread de rede gerenciada pela biblioteca).
- Versões exatas fixadas no `requirements.txt` ([ADR-028](ADR-028-versoes-fixadas.md)).

## Justificativa

Código síncrono lê de cima para baixo e pode ser projetado em aula. O pymodbus é a biblioteca Modbus mais usada em Python; o paho-mqtt é o cliente MQTT de referência da Eclipse. A API do pymodbus mudou entre versões 3.x (por exemplo, o nome do argumento de endereço do escravo), o que reforça fixar a versão.

## Consequências

- Positivas: uma pessoa que leu o `cliente.js` da Aula 1 reconhece a mesma sequência (conectar, ler, escrever).
- Negativas: a coordenação entre a thread do MQTT e o laço principal precisa ser explícita ([ADR-009](ADR-009-concorrencia-no-gateway.md)).

## Verificação

- `pip install -r requirements.txt` num venv limpo instala tudo sem compilar nada.
- Teste de integração ([ADR-027](ADR-027-testes-e-aceitacao.md)) roda com as versões fixadas.

## Relacionadas

[ADR-009](ADR-009-concorrencia-no-gateway.md), [ADR-016](ADR-016-stack-do-middleware.md), [ADR-028](ADR-028-versoes-fixadas.md)
