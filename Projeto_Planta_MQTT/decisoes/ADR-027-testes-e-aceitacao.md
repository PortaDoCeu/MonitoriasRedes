# ADR-027: Testes e ensaio de aceitação

**Status:** Aceita

## Contexto

Várias decisões só têm valor se funcionarem na hora: watchdog, rejeição de comando, reconexão, ACL. A única forma de confiar nelas na frente da turma é tê-las testado antes.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Testar manualmente na véspera | Nada a escrever | Não se repete igual; esquece casos |
| Só testes unitários | Rápidos | Não pegam erro de integração (tópico errado, ACL) |
| **Três níveis: unitário, integração com simulado, ensaio na bancada** | Cada nível pega uma classe de defeito | Tempo para escrever e rodar |

## Decisão

| Nível | Ferramenta | O que cobre | Quando |
|---|---|---|---|
| Unitário | pytest | Conversões da tabela 5.8, validação da [ADR-011](ADR-011-validacao-de-comandos.md), decodificação dos bits de status | A cada mudança |
| Integração | pytest + `clp_simulado.py` + Mosquitto real | Ciclo completo leitura, publicação, comando, resposta, gravação no banco; ACL | A cada mudança no contrato |
| Ensaio de aceitação | Roteiro em `ensaio.md` na bancada real | Cada item de Verificação das ADRs e cada linha da seção 7 do Arquitetura.md | Antes da primeira aula e depois de qualquer mudança no CLP |

O ensaio de aceitação tem uma tabela com: item, ADR de origem, procedimento, resultado esperado, resultado obtido, data. A aula só acontece com todos os itens aprovados ou com os reprovados registrados como risco conhecido.

## Justificativa

O ensaio transforma os campos "Verificação" desta pasta num roteiro executável. Rodar o mesmo roteiro com o simulado e com o CLP real também valida a [ADR-002](ADR-002-modo-simulado.md).

## Consequências

- Positivas: as falhas da seção 7 do Arquitetura.md são exercitadas antes de acontecerem em aula.
- Negativas: o ensaio completo na bancada leva tempo (estimado em 1 h).

## Verificação

- `pytest` passa sem falhas no notebook da aula.
- `ensaio.md` preenchido e datado antes da primeira aula.

## Relacionadas

Todas as ADRs com seção de Verificação; [ADR-002](ADR-002-modo-simulado.md), [Arquitetura.md, seção 7](../Arquitetura.md)
