# ADR-003: Premissas de hardware da planta

**Status:** Aceita com premissa

## Contexto

O contrato de dados e a lógica do CLP dependem de detalhes da bancada que ainda não foram conferidos: modelo da CPU, como o termopar é lido, como a velocidade é comandada, a velocidade nominal do motor e a faixa de temperatura. Para não travar o projeto, os valores são assumidos agora e validados na bancada.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Esperar o levantamento da bancada | Nenhuma suposição | Bloqueia o projeto inteiro |
| Deixar como parâmetros sem valor | Flexível | Nada pode ser testado; o simulado não tem valores para simular |
| **Assumir valores típicos, registrados como premissa** | Projeto avança; cada premissa tem ponto de verificação claro | Retrabalho localizado se uma premissa cair |

## Decisão

| Item | Premissa | Onde conferir |
|---|---|---|
| CPU | S7-1200 CPU 1214C | Etiqueta frontal da CPU e Device configuration no TIA Portal |
| Saída analógica para o inversor | Signal board SB 1232 AQ, saída em corrente (0 a 20 mA, usada de 4 a 20 mA) | A 1214C não tem saída analógica integrada (a confirmar no manual do sistema S7-1200) |
| Termopar | Tipo K, lido por módulo SM 1231 TC | Etiqueta do sensor e do módulo. Resolução do valor lido pelo módulo a confirmar no manual do SM 1231 |
| Inversor | Referência de velocidade por entrada analógica 4 a 20 mA; partida e parada por entrada digital; saída digital de falha ligada numa entrada do CLP | Manual e parametrização do inversor da bancada |
| Realimentação de velocidade | Não existe; HR1 é cópia de HR3 (velocidade estimada) | Verificar se o inversor tem saída analógica ligada ao CLP |
| Motor | Trifásico, 4 polos, 60 Hz | Placa do motor |
| `VEL_MAX` | 1700 rpm (abaixo da nominal típica de um motor de 4 polos em 60 Hz, em torno de 1720 a 1750 rpm) | Placa do motor: usar a rotação nominal arredondada para baixo |
| Faixa válida de temperatura | 0 a 150 °C | Tipo de termopar e o que aquece a bancada |
| Limite de alarme (código de falha 4) | 80 °C | Definir com o professor responsável pela bancada |
| Sensor aberto (código de falha 5) | Valor lido fora da faixa válida | Comportamento do SM 1231 com sensor desconectado (a confirmar no manual) |
| Botão de emergência e chave local/remoto | Existem e estão ligados em entradas do CLP; emergência também corta a potência fisicamente | Inspeção da bancada |

## Justificativa

Os valores são os mais comuns para uma bancada didática com S7-1200 e inversor. Cada um aparece em um único lugar do código (constante no CLP e variável no `config.env`), então trocar uma premissa não se espalha pelo projeto.

## Consequências

- Positivas: o projeto, o simulado e os testes podem começar já.
- Negativas: se a CPU for outra (por exemplo 1215C, que tem saída analógica integrada), muda o hardware da saída mas não o contrato. Se não houver módulo de termopar, é preciso um transmissor externo para 4 a 20 mA e uma nova escala no CLP.

## Verificação

Checklist de levantamento da bancada, preenchido antes da primeira aula, com uma linha por item da tabela acima e o valor real encontrado. Toda premissa que cair gera uma revisão desta ADR e das que ela afeta.

## Relacionadas

[ADR-004](ADR-004-papeis-modbus-e-db.md), [ADR-005](ADR-005-seguranca-funcional-no-clp.md), [ADR-006](ADR-006-contrato-de-dados.md), [Arquitetura.md, seção 12](../Arquitetura.md)
