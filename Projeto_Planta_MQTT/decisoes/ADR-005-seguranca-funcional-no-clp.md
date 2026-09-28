# ADR-005: Segurança funcional fica no CLP e no hardware

**Status:** Aceita

## Contexto

Um motor comandado por um celular pode girar quando não deveria: comando errado, app travado, notebook que congela com o motor ligado, alguém mexendo na bancada enquanto outro aperta "ligar". O software acima do CLP (gateway, broker, app) roda num notebook comum e pode falhar a qualquer momento.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Validar tudo no gateway | Um lugar só | Se o notebook travar, nada protege a planta |
| Validar só no CLP | Proteção onde está a planta | Comandos inválidos chegam até o CLP; erro só aparece tarde |
| **Camadas: hardware, depois CLP, depois gateway** | Cada camada cobre a falha da de cima | Regras duplicadas em dois lugares (gateway e CLP) |

## Decisão

| Camada | Proteção |
|---|---|
| Hardware | Botão de emergência corta a potência do inversor fisicamente, sem passar por software |
| CLP | Chave local/remoto: em local, ignora HR10 e HR11 |
| CLP | Limita a referência a `VEL_MAX` e publica o valor aplicado em HR3 |
| CLP | Watchdog: se HR12 não mudar por 3 s, para o motor, liga o bit 3 do HR2 e grava código 2 no HR4 |
| CLP | Falha travada: com código de falha diferente de 0, o motor não liga até receber o comando 2 (reconhecer) com a causa já resolvida |
| CLP | Temperatura acima de 80 °C para o motor (código 4) |
| Gateway | Rejeita comando fora da faixa antes de escrever ([ADR-011](ADR-011-validacao-de-comandos.md)) |

## Justificativa

A regra é que nenhuma camada confie na de cima. O CLP é o componente determinístico e mais próximo da planta; o hardware é o único que funciona até com o CLP em falha. A NR-12 exige dispositivo de parada de emergência em máquinas, e ele precisa agir sobre a potência, não sobre uma mensagem de rede.

## Consequências

- Positivas: travar o notebook, derrubar o Wi-Fi ou mandar um comando absurdo nunca deixa o motor fora de controle.
- Negativas: as regras de faixa existem no gateway e no CLP. Se `VEL_MAX` mudar, precisa mudar nos dois ([ADR-025](ADR-025-configuracao-e-segredos.md) mantém um único lugar do lado do gateway).

## Verificação

Cada linha é um item do ensaio de aceitação ([ADR-027](ADR-027-testes-e-aceitacao.md)):
- matar o processo do gateway com o motor ligado: motor para em até 3 s;
- chave em local e comando "ligar" pelo app: resposta `rejeitado` e motor parado;
- escrever HR10 = 5000 direto no CLP (gateway desligado, cliente de teste): HR3 fica em `VEL_MAX` e o bit 4 do HR2 liga;
- apertar a emergência: motor para mesmo com o CLP comandando partida.

## Relacionadas

[ADR-003](ADR-003-premissas-de-hardware.md), [ADR-006](ADR-006-contrato-de-dados.md), [ADR-010](ADR-010-ciclo-e-temporizacao.md), [ADR-011](ADR-011-validacao-de-comandos.md), [Arquitetura.md, seções 6 e 7](../Arquitetura.md)
