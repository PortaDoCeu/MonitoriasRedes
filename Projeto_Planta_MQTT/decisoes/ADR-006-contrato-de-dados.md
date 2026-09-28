# ADR-006: Contrato de dados congelado

**Status:** Aceita

## Contexto

Quatro programas precisam concordar sobre os mesmos números: o programa do CLP, `gateway.py`, `middleware.py` e o app. Qualquer divergência (um registrador trocado, uma escala esquecida, um nome de tópico diferente) gera um defeito silencioso: o sistema funciona, mas mostra o valor errado.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Cada programa define seus endereços | Rápido no começo | Divergência garantida |
| Descoberta automática (por exemplo, publicar o mapa no broker) | Flexível | Complexidade sem ganho para um mapa fixo de 10 itens |
| **Contrato único documentado e congelado** | Fonte única de verdade; testável | Mudança exige tocar quatro programas |

## Decisão

O contrato é a [seção 5 do Arquitetura.md](../Arquitetura.md) e fica congelado:
- holding registers HR0 a HR9 para leitura e HR10 a HR19 para escrita, base 0;
- números decimais como inteiro × 10, sem ponto flutuante;
- tópicos `bancada1/<tipo>/<grandeza>`, com QoS e retenção da tabela 5.6;
- comandos nunca retidos;
- payloads JSON da seção 5.7, com `ts` em UTC ISO 8601 gerado pelo gateway.

Regra de mudança: qualquer alteração no contrato é feita num único commit que muda o Arquitetura.md, o `gateway.py`, o `clp_simulado.py`, o `middleware.py`, o app e o programa do CLP (exportado), e atualiza esta ADR.

## Justificativa

Um mapa pequeno e fixo não precisa de mecanismo dinâmico. O que precisa é disciplina: um lugar só, e uma regra que impeça mudar uma ponta sem as outras.

## Consequências

- Positivas: testes podem conferir cada conversão contra a tabela 5.8.
- Negativas: nenhuma flexibilidade em tempo de execução, o que é aceitável.

## Verificação

- Teste automatizado que lê o `clp_simulado.py` com valores conhecidos e confere que cada tópico publicado tem o valor, a unidade e o nome esperados pela tabela 5.8.
- Revisão: nenhum endereço numérico literal no código fora de um único módulo de constantes (`contrato.py`) compartilhado por gateway e simulado.

## Relacionadas

[ADR-004](ADR-004-papeis-modbus-e-db.md), [ADR-011](ADR-011-validacao-de-comandos.md), [ADR-013](ADR-013-configuracao-do-broker.md), [ADR-027](ADR-027-testes-e-aceitacao.md), [Arquitetura.md, seção 5](../Arquitetura.md)
