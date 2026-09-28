# ADR-023: Fonte de horário

**Status:** Aceita

## Contexto

Cada medição e cada comando têm um horário. Se horários vierem de relógios diferentes (CLP, notebook, celular), o histórico fica fora de ordem e os atrasos medidos na [ADR-001](ADR-001-ambiente-e-requisitos.md) não fazem sentido. Sem internet, não há NTP público.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Relógio do CLP (lido por Modbus) | Horário da própria planta | Relógio do S7-1200 costuma estar desacertado; exige mais registradores |
| Horário do celular | Nenhum | 40 relógios diferentes |
| **Relógio do notebook, carimbado pelo gateway** | Uma fonte só; gateway e middleware no mesmo host | Se o relógio do notebook estiver errado, todos os horários ficam deslocados igualmente |

## Decisão

- O gateway gera o `ts` no instante em que a leitura Modbus retorna, em UTC ISO 8601 com precisão de milissegundos.
- O middleware nunca gera horário para medição; usa o `ts` do JSON.
- Para comandos, o middleware grava o `ts` da resposta do gateway.
- O app converte UTC para o horário local só na exibição.
- O relógio do CLP não é usado.

## Justificativa

Uma única fonte de horário torna tudo comparável. Um deslocamento constante do relógio do notebook não afeta atrasos nem ordem, só o horário absoluto.

## Consequências

- Positivas: histórico sempre ordenado.
- Negativas: o horário absoluto depende do notebook estar acertado antes de sair da internet.

## Verificação

- Checklist pré-aula: relógio do notebook sincronizado (Configurações, Hora, "Sincronizar agora") ainda com internet.
- Nenhuma linha em `medicoes` com `ts` fora de ordem em relação ao `id`.

## Relacionadas

[ADR-001](ADR-001-ambiente-e-requisitos.md), [ADR-006](ADR-006-contrato-de-dados.md), [ADR-017](ADR-017-banco-de-dados.md)
