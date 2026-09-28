# ADR-002: Modo simulado obrigatório

**Status:** Aceita

## Contexto

A bancada nem sempre está disponível ou funcionando no dia da aula. Além disso, o gateway e o middleware precisam ser desenvolvidos e testados em casa, longe do CLP. Sem um substituto do CLP, qualquer defeito de hardware cancela a aula e todo teste depende do laboratório.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Só hardware real | Nada a mais para manter | Aula refém da bancada; impossível testar fora do lab |
| PLCSIM no TIA Portal | Roda o mesmo programa do CLP | O PLCSIM comum não expõe Modbus TCP para a rede real (a confirmar para a versão disponível); exige licença e TIA aberto |
| Simulador Modbus genérico de terceiros | Pronto | Não implementa a lógica do contrato (status, falhas, watchdog) |
| **`clp_simulado.py` com pymodbus** | Mesmo mapa e mesma lógica essencial; mesmo Python do resto do projeto; roda em qualquer máquina | Mais um programa para manter em sincronia com o contrato |

## Decisão

Criar `clp_simulado.py`, um servidor Modbus TCP com pymodbus que:
- expõe o mesmo mapa HR0 a HR19 do [contrato](ADR-006-contrato-de-dados.md);
- simula temperatura (valor que varia lentamente com ruído), velocidade seguindo a referência com rampa, bits de status e códigos de falha;
- implementa o watchdog de heartbeat de 3 s e o comando 2 (reconhecer falha);
- escuta em `127.0.0.1:5020` por padrão (porta acima de 1024 para não exigir privilégio).

O gateway troca entre CLP real e simulado apenas pelo `config.env` (`MODBUS_HOST` e `MODBUS_PORT`), sem mudança de código.

## Justificativa

A contingência deixa de ser "uma captura .pcap pronta" e passa a ser o sistema inteiro funcionando, só que com a planta simulada. A mesma peça serve de dublê nos testes de integração ([ADR-027](ADR-027-testes-e-aceitacao.md)).

## Consequências

- Positivas: aula acontece mesmo sem bancada; desenvolvimento e testes independem do laboratório.
- Negativas: o simulado pode divergir do CLP real. Mitigação: o ensaio de aceitação roda nos dois e qualquer mudança no contrato exige mudar o simulado no mesmo commit.

## Verificação

- Com `MODBUS_HOST=127.0.0.1` e `MODBUS_PORT=5020`, o sistema completo funciona sem nenhum CLP na rede.
- Parar o gateway por 3 s faz o simulado ligar o bit 3 do HR2 e zerar a velocidade, igual ao CLP real.
- O mesmo roteiro de aceitação passa nos dois modos.

## Relacionadas

[ADR-001](ADR-001-ambiente-e-requisitos.md), [ADR-005](ADR-005-seguranca-funcional-no-clp.md), [ADR-006](ADR-006-contrato-de-dados.md), [ADR-025](ADR-025-configuracao-e-segredos.md), [ADR-027](ADR-027-testes-e-aceitacao.md)
