# ADR-011: Validação de comandos e respostas

**Status:** Aceita

## Contexto

Todo comando chega de um celular, pela rede, como texto. Pode vir malformado, com tipo errado, fora da faixa, ou em um momento em que a planta está em modo local. O app precisa saber o que aconteceu com cada comando.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Escrever qualquer valor e deixar o CLP limitar | Simples | Aluno não recebe retorno; valores absurdos chegam ao CLP |
| Responder só sucesso ou erro | Simples | Não distingue "você pediu errado" de "a rede falhou" |
| **Validar no gateway e responder com três resultados e motivo** | Retorno claro; nada inválido chega ao CLP | Um tópico e um formato a mais |

## Decisão

Ordem de validação, parando na primeira falha:

| Passo | Condição | Resultado se falhar | `motivo` |
|---|---|---|---|
| 1 | JSON válido com `id` (texto) e `valor` (número) | `rejeitado` | `formato invalido` |
| 2 | Tópico `velocidade`: `valor` entre 0 e `VEL_MAX` | `rejeitado` | `fora da faixa` |
| 2 | Tópico `motor`: `valor` é 0, 1 ou 2 | `rejeitado` | `valor invalido` |
| 3 | Último status lido tem `modo_remoto = true` | `rejeitado` | `modo local` |
| 4 | Escrita FC 6 sem exceção e sem timeout | `falhou` | `sem resposta do CLP` ou o código de exceção Modbus |

Se passar em tudo: `executado`. O `valor` de velocidade é arredondado para inteiro antes da escrita. A resposta sempre repete o `id` recebido; comando sem `id` válido é descartado e registrado no log, porque não há como respondê-lo.

## Justificativa

Separar `rejeitado` (o pedido estava errado) de `falhou` (o pedido estava certo, mas a comunicação falhou) é o que permite ao aluno e ao monitor saber onde olhar. O passo 3 duplica a checagem que o CLP também faz, mas evita escrever e dá uma resposta imediata e explicada.

## Consequências

- Positivas: toda linha da tabela `comandos` tem um resultado explicado.
- Negativas: o gateway precisa de `VEL_MAX` e do último status em memória.

## Verificação

Testes unitários com pytest cobrindo cada linha da tabela: JSON quebrado, `valor` texto, -1, `VEL_MAX` + 1, motor = 3, modo local, CLP desligado. Cada caso produz exatamente o `resultado` e o `motivo` da tabela.

## Relacionadas

[ADR-005](ADR-005-seguranca-funcional-no-clp.md), [ADR-006](ADR-006-contrato-de-dados.md), [ADR-009](ADR-009-concorrencia-no-gateway.md), [ADR-020](ADR-020-interacao-de-comando.md)
