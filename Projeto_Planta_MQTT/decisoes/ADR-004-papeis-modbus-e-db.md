# ADR-004: Papéis Modbus e bloco de dados do CLP

**Status:** Aceita

## Contexto

Alguém precisa ser cliente e alguém precisa ser servidor Modbus. Na Aula 2 o CLP foi configurado como servidor (`MB_SERVER`) com um DB `Array[0..99] of Word`, e o `cliente.js` fazia o papel de cliente. O quadro da aula mostrava um "Modbus Server" dentro do Node-RED, o que colocaria dois servidores frente a frente.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| CLP cliente (`MB_CLIENT`), gateway servidor | CLP decide quando enviar | Refaz toda a configuração da Aula 2; lógica de comunicação espalhada no programa do CLP |
| **CLP servidor (`MB_SERVER`), gateway cliente** | Reaproveita a Aula 2 inteira; o gateway controla o ritmo e é o único ponto de acesso | O CLP não "empurra" eventos; tudo é por varredura (polling) |
| DB novo de 20 registradores | Área exposta mínima | Diverge do material da Aula 2 |
| **Reaproveitar o DB `Array[0..99] of Word`** | Mesmo DB da Aula 2 | 80 registradores expostos sem uso |

## Decisão

- O CLP é servidor Modbus TCP na porta 502, com a biblioteca que ele tiver (legada ou v4.0+), configurado exatamente como na Aula 2.
- O `gateway.py` é o único cliente.
- O DB de holding registers continua `Array[0..99] of Word`. O contrato usa HR0 a HR19; HR20 a HR99 ficam reservados, e o programa do CLP ignora qualquer valor escrito neles.
- Uma única instância de `MB_SERVER`, portanto uma única conexão TCP aceita. Pelo manual da Siemens (Entry-ID 102020340), cada instância atende uma conexão; a confirmar no TIA Portal da bancada.

## Justificativa

Continuidade didática com a Aula 2 e ponto único de acesso. Com uma única conexão aceita, o próprio CLP recusa um segundo cliente enquanto o gateway estiver conectado, o que reforça a regra "só o gateway fala com o CLP" sem depender de firewall.

## Consequências

- Positivas: nenhuma configuração nova no CLP além da lógica da aplicação.
- Negativas: enquanto o gateway estiver conectado, os alunos não conseguem rodar o `cliente.js` da Aula 2 contra o mesmo CLP. Isso é intencional e pode ser mostrado em aula. Para demonstrações com dois clientes, seria preciso uma segunda instância de `MB_SERVER` com outra porta, o que fica fora deste projeto.

## Verificação

- Com o gateway conectado, tentar conectar o `cliente.js` na porta 502: a conexão é recusada ou não recebe resposta.
- Escrever em HR50 com um cliente de teste (gateway desligado): nada muda no comportamento do CLP.

## Relacionadas

[ADR-006](ADR-006-contrato-de-dados.md), [ADR-007](ADR-007-protecao-do-clp.md), [ADR-009](ADR-009-concorrencia-no-gateway.md), [Arquitetura.md, seção 5.1](../Arquitetura.md)
