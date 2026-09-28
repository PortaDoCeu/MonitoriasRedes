# ADR-001: Ambiente-alvo e requisitos não funcionais

**Status:** Aceita

## Contexto

"Produção", neste projeto, é o sistema funcionando de ponta a ponta durante uma monitoria, com a turma acompanhando e usando o próprio celular. Não é uma fábrica. Mas é uma apresentação ao vivo: se algo falhar na frente da turma, a aula perde o ponto. Sem requisitos escritos, cada decisão técnica seguinte fica sem critério para ser julgada.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Não fixar requisitos, ajustar na hora | Nenhum esforço prévio | Nenhuma decisão pode ser verificada; falhas aparecem durante a aula |
| Requisitos de ambiente industrial (24/7, redundância) | Rigor máximo | Custo e complexidade fora do alcance de uma monitoria; esconde o conteúdo principal |
| **Requisitos da demonstração em aula, com números** | Verificáveis antes da aula, proporcionais ao uso real | Não cobrem operação contínua |

## Decisão

| Requisito | Valor |
|---|---|
| Duração de operação contínua sem intervenção | 3 h (uma aula) |
| Hospedagem | Um único notebook roda broker, gateway, middleware e banco |
| Dependência de internet | Nenhuma. Tudo funciona com a rede do laboratório desconectada da internet |
| Clientes simultâneos | Até 40 celulares com o app aberto |
| Atraso da telemetria (leitura no CLP até a tela) | ≤ 2 s |
| Atraso do comando (toque no app até a resposta na tela) | ≤ 1 s |
| Tempo para subir o sistema do zero | ≤ 5 min, seguindo um único script |
| Contingência | Aula executável sem a bancada física (ver [ADR-002](ADR-002-modo-simulado.md)) |
| Entregável da aula | Arquivo CSV com os dados coletados (ver [ADR-018](ADR-018-api-http.md)) |

## Justificativa

Os números vêm do uso: ciclo de leitura de 1 s mais transporte cabe em 2 s; 1 s de resposta a comando é o limite em que o aluno ainda percebe causa e efeito. 40 celulares cobre uma turma cheia com folga. A exigência de funcionar sem internet vem da realidade do laboratório e elimina toda dependência de CDN ou serviço externo.

## Consequências

- Positivas: toda ADR seguinte tem um alvo mensurável; o ensaio de aceitação ([ADR-027](ADR-027-testes-e-aceitacao.md)) tem o que medir.
- Negativas: nada aqui garante operação por dias; redundância e alta disponibilidade ficam fora do escopo, de forma explícita.

## Verificação

- Ensaio de 3 h com o sistema rodando sem intervenção, sem reinício de nenhum processo.
- Com o cabo de internet desconectado, abrir o app num celular e ver dados ao vivo.
- Medir o atraso: comparar o `ts` do JSON com o horário de chegada na tela (console do navegador), p95 ≤ 2 s.
- Cronometrar `iniciar.ps1` do zero até o primeiro dado na tela: ≤ 5 min.

## Relacionadas

[ADR-002](ADR-002-modo-simulado.md), [ADR-010](ADR-010-ciclo-e-temporizacao.md), [ADR-019](ADR-019-tecnologia-do-app.md), [ADR-024](ADR-024-execucao-dos-servicos.md), [ADR-027](ADR-027-testes-e-aceitacao.md), [Arquitetura.md, seção 1](../Arquitetura.md)
