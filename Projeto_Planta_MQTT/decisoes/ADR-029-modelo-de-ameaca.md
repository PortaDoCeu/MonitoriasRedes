# ADR-029: Modelo de ameaça e nível de segurança alvo

**Status:** Aceita

## Contexto

As decisões de segurança anteriores precisam de um alvo comum: contra quem o sistema se protege. Sem isso, não dá para dizer se uma medida é suficiente ou exagerada. A IEC 62443 define níveis de segurança (SL) de 1 a 4, do atacante casual ao atacante com muitos recursos.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Sem alvo definido | Nenhum | Medidas arbitrárias; impossível avaliar |
| SL 2 ou superior (atacante intencional com meios simples) | Mais próximo de uma planta real | Exige TLS, autenticação forte e segmentação real, contra a [ADR-015](ADR-015-sem-tls-na-monitoria.md) e a [ADR-021](ADR-021-topologia-e-enderecamento.md) |
| **SL 1 (violação casual ou acidental)** | Coerente com uma aula; atingível | Não resiste a um aluno que decida atacar de propósito |

## Decisão

Alvo: **SL 1** para a demonstração. O sistema deve impedir que alguém, por engano ou curiosidade, comande a planta, reprograme o CLP ou falsifique dados.

| Ameaça | Exemplo | Tratamento |
|---|---|---|
| Comando por engano | Aluno toca em "ligar" | Não tem `app_operador` ([ADR-014](ADR-014-autenticacao-e-acl.md)) |
| Comando perigoso | Referência absurda | Validação no gateway e limite no CLP ([ADR-005](ADR-005-seguranca-funcional-no-clp.md), [ADR-011](ADR-011-validacao-de-comandos.md)) |
| Planta sem supervisão | Notebook trava com motor ligado | Watchdog no CLP ([ADR-005](ADR-005-seguranca-funcional-no-clp.md)) |
| Reprogramação do CLP | TIA Portal de um aluno | Proteção de acesso ([ADR-007](ADR-007-protecao-do-clp.md)) |
| Segundo cliente Modbus | `cliente.js` apontado para o CLP | Conexão única ocupada ([ADR-004](ADR-004-papeis-modbus-e-db.md)) |
| Dado falso no app | Publicar telemetria | ACL ([ADR-014](ADR-014-autenticacao-e-acl.md)) |

Fora do escopo (SL 2 ou mais), registrado como risco aceito:
- captura da senha do operador no Wi-Fi ([ADR-015](ADR-015-sem-tls-na-monitoria.md));
- acesso Modbus direto ao CLP quando o gateway estiver desligado, a partir da mesma sub-rede ([ADR-021](ADR-021-topologia-e-enderecamento.md));
- negação de serviço contra o broker ou o AP.

Qualquer demonstração de ataque a esses pontos segue a regra da monitoria: só em bancada isolada dedicada, nunca em rede de produção.

## Justificativa

Definir SL 1 explica por que TLS e VLAN ficaram de fora sem que isso pareça descuido: é uma escolha registrada, com o que seria necessário para subir de nível. A lista de fora do escopo vira roteiro natural para as aulas de ataque e defesa do Bloco 2 do roadmap.

## Consequências

- Positivas: cada risco tem dono (uma ADR) ou está explicitamente aceito.
- Negativas: o sistema não deve ser apresentado como seguro contra ataque intencional, e o material da aula precisa dizer isso.

## Verificação

- Cada linha da tabela de ameaças tem um item correspondente no ensaio de aceitação ([ADR-027](ADR-027-testes-e-aceitacao.md)).
- A tabela de riscos aceitos do [README](README.md) contém os três itens fora do escopo.

## Relacionadas

[ADR-004](ADR-004-papeis-modbus-e-db.md), [ADR-005](ADR-005-seguranca-funcional-no-clp.md), [ADR-007](ADR-007-protecao-do-clp.md), [ADR-014](ADR-014-autenticacao-e-acl.md), [ADR-015](ADR-015-sem-tls-na-monitoria.md), [ADR-021](ADR-021-topologia-e-enderecamento.md), [Arquitetura.md, seção 6](../Arquitetura.md)
