# Componente Output

## Objetivo

Este componente transforma dados ja analisados em linhas JSON enviadas pela UART.

Ele existe para separar claramente duas etapas:

- entender o frame
- exibir o frame

Essa separacao facilita manutencao, testes e futuras mudancas no formato de saida.

## O que este componente faz

- Converte o tipo de captura em um nome legivel
- Mantem o formato JSON esperado pelo projeto
- Imprime uma linha JSON por frame analisado

## Conceitos importantes

- `JSON` e um formato textual estruturado, facil de ler por humanos e por ferramentas.
  Ele e util para logs, integracao com scripts e analise posterior.

- `UART` e a interface serial usada para mandar o texto do ESP32 para o computador.
  Quando o sniffer imprime um JSON com `printf`, esse texto chega no monitor serial.

- Este componente nao interpreta pacotes.
  Ele apenas recebe uma estrutura pronta e a serializa.

## API publica

- `sniffer_emit_json_record()`
  Recebe um frame capturado e um frame analisado e escreve a linha JSON correspondente.

## Arquivo principal

- `sniffer_output.c`

## Estrategia de projeto

Este modulo deve continuar sem estado interno.
Ele nao precisa conhecer tasks, ring buffer, Ethernet ou L2 TAP.
Ele so precisa saber formatar os dados recebidos.

## Quando mexer aqui

Voce altera este componente quando quiser:

- mudar o formato do JSON
- renomear campos
- adicionar ou remover campos de saida
- trocar o destino da impressao no futuro
