# Componente App

## Objetivo

Este componente e o ponto de entrada da aplicacao.
Ele existe para manter o `app_main()` simples, curto e facil de ler.

Em vez de concentrar toda a logica em um unico arquivo grande, o `app_main()` apenas organiza a ordem de inicializacao e delega o trabalho real para os outros modulos.

## O que este componente faz

- Inicializa a NVS
- Inicializa o `esp_netif`
- Inicializa o loop de eventos padrao do ESP-IDF
- Registra a interface L2 TAP na VFS
- Inicia a Ethernet
- Aguarda a Ethernet ficar pronta
- Inicia o runtime do sniffer

## Fluxo de inicializacao

1. A aplicacao liga e entra em `app_main()`.
2. A NVS e inicializada.
3. O sistema de rede do ESP-IDF e preparado.
4. A interface L2 TAP e registrada.
5. A Ethernet da placa e iniciada.
6. O codigo espera a Ethernet subir.
7. O runtime do sniffer e iniciado.

## Conceitos importantes

- `NVS` significa `Non-Volatile Storage`.
  E a area de armazenamento persistente do ESP32.
  Ela guarda dados que precisam sobreviver a reboot, como configuracoes e calibracoes.

- `esp_netif` e a camada de abstracao de interfaces de rede do ESP-IDF.
  Ela representa interfaces como Ethernet e Wi-Fi e conecta o driver de rede com a pilha TCP/IP.

- `VFS` significa `Virtual File System`.
  No ESP-IDF, isso permite acessar certos recursos por uma interface parecida com arquivos.
  No nosso caso, o L2 TAP aparece como `/dev/net/tap`.

- `L2 TAP` e uma interface que permite ler e escrever quadros Ethernet em nivel 2.
  Ou seja, antes de TCP, UDP ou aplicacoes.
  Isso e exatamente o que o sniffer precisa para observar trafego bruto.

## Arquivo principal

- `l2tap_sniffer_main.c`

## O que nao deve ficar aqui

- Parse de pacotes
- Emissao de JSON
- Leitura direta de frames
- Controle detalhado de Ethernet

Essas responsabilidades pertencem aos outros componentes.

## Observacao de projeto

Se este modulo crescer demais, isso normalmente significa que alguma responsabilidade escapou do lugar certo e deve voltar para `eth`, `runtime`, `parser` ou `output`.
