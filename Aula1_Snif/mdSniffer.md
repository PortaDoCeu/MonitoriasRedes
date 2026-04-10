# l2tap_sniffer

Biblioteca open source para captura e análise de quadros Ethernet em nível 2 usando `ESP-NETIF L2 TAP` no ESP-IDF.

O objetivo da biblioteca é servir como base para novos sniffers. Em vez de cada projeto reimplementar bring-up Ethernet, abertura de filtros L2 TAP, tasks de captura, parser de quadros e callbacks, a aplicação hospedeira configura a biblioteca e recebe os frames por eventos e callbacks.

Hoje a biblioteca está no componente:

- [components/l2tap_sniffer](c:/Users/CLP2-U001/Documents/l2tap_industrial_sniffer/l2tap/components/l2tap_sniffer)

O projeto também mantém um exemplo de uso em:

- [main/src/app/l2tap_sniffer_main.c](c:/Users/CLP2-U001/Documents/l2tap_industrial_sniffer/l2tap/main/src/app/l2tap_sniffer_main.c)

## Visão Geral

A biblioteca cuida de:

- inicialização do backend Ethernet suportado
- espera do link Ethernet
- abertura dos descritores `/dev/net/tap`
- criação das tasks de captura, análise e estatísticas
- parsing de ARP, IPv4, TCP, UDP, VLAN e QinQ
- detecção básica de protocolos industriais
- entrega dos dados para a aplicação via callbacks

A aplicação hospedeira continua responsável por:

- inicializar `NVS`
- inicializar `esp_netif`
- criar o event loop padrão
- registrar o `ESP-VFS L2 TAP`
- montar a configuração da biblioteca
- decidir o que fazer com os frames recebidos

## O Que é Cada Coisa

- `L2 TAP`: mecanismo do ESP-IDF para acessar quadros Ethernet no nível 2, antes da interpretação tradicional por pilhas IP.
- `NVS`: armazenamento persistente do ESP32, usado pelo sistema e por aplicações.
- `VFS`: camada de sistema de arquivos virtual do ESP-IDF. É ela que permite acessar `/dev/net/tap` com `open()`, `read()` e `ioctl()`.
- `EMAC`: controlador Ethernet do chip.
- `PHY`: circuito físico Ethernet responsável pela camada elétrica do enlace.
- `RMII`: interface física entre MAC e PHY em placas com Ethernet externa.
- `callback`: função fornecida pela aplicação e chamada pela biblioteca quando algo acontece.
- `handle`: referência opaca para a instância criada da biblioteca.

## Estado Atual de Compatibilidade

No estado atual, a biblioteca está validada para:

- `ESP32`
- backend Ethernet com `EMAC` interno
- interface `RMII`
- PHY `RTL8201`

O parser e o runtime foram escritos de forma reaproveitável, mas o backend Ethernet atual ainda é específico desse caminho de hardware.

## Arquivos Públicos da Biblioteca

- [l2tap_sniffer.h](c:/Users/CLP2-U001/Documents/l2tap_industrial_sniffer/l2tap/components/l2tap_sniffer/include/l2tap_sniffer.h)
- [l2tap_sniffer_types.h](c:/Users/CLP2-U001/Documents/l2tap_industrial_sniffer/l2tap/components/l2tap_sniffer/include/l2tap_sniffer_types.h)

## Fluxo Básico de Uso

### 1. Inicialize o ambiente do ESP-IDF

Antes de usar a biblioteca, a aplicação deve preparar a infraestrutura básica:

```c
ESP_ERROR_CHECK(nvs_flash_init());
ESP_ERROR_CHECK(esp_netif_init());
ESP_ERROR_CHECK(esp_event_loop_create_default());
ESP_ERROR_CHECK(esp_vfs_l2tap_intf_register(NULL));
```

### 2. Monte a configuração

Use os helpers de configuração padrão:

```c
l2tap_sniffer_config_t config = l2tap_sniffer_config_default();
```

Depois preencha filtros, backend Ethernet e callbacks.

## Como Configurar a Biblioteca

Esta é a parte mais importante para quem vai reutilizar o componente.

A configuração principal fica em:

```c
l2tap_sniffer_config_t config;
```

Ela reúne cinco grupos:

- `interface_name`: nome da interface L2 TAP
- `filters`: quais EtherTypes serão capturados
- `runtime`: tamanhos de buffer e temporização interna
- `parser`: o que será interpretado no frame
- `eth`: parâmetros do backend Ethernet
- `callbacks`: como a aplicação recebe os dados

### Configuração mínima

O caminho mais simples é começar com os defaults e preencher só o necessário:

```c
l2tap_sniffer_config_t config = l2tap_sniffer_config_default();

static const l2tap_sniffer_filter_t filters[] = {
    { "ipv4", L2TAP_SNIFFER_ETH_TYPE_IPV4 },
    { "arp", L2TAP_SNIFFER_ETH_TYPE_ARP },
};

config.filters = filters;
config.filter_count = 2;

config.eth.power_gpio = 12;
config.eth.mdc_gpio = 23;
config.eth.mdio_gpio = 18;
config.eth.phy_addr = 0;
config.eth.rmii_clk_gpio = 0;
config.eth.phy_reset_gpio = -1;
config.eth.phy = L2TAP_SNIFFER_PHY_RTL8201;

config.callbacks.on_parsed_frame = on_frame;
```

Esse exemplo já é suficiente para:

- subir a Ethernet
- abrir os filtros L2 TAP
- parsear os quadros
- entregar os frames parseados ao callback

### Exemplo com configuração explícita de todos os blocos

```c
l2tap_sniffer_config_t config = l2tap_sniffer_config_default();

static const l2tap_sniffer_filter_t filters[] = {
    { "ipv4", L2TAP_SNIFFER_ETH_TYPE_IPV4 },
    { "arp", L2TAP_SNIFFER_ETH_TYPE_ARP },
    { "vlan", L2TAP_SNIFFER_ETH_TYPE_VLAN },
    { "qinq", L2TAP_SNIFFER_ETH_TYPE_QINQ },
    { "profinet", L2TAP_SNIFFER_ETH_TYPE_PROFINET },
    { "ethercat", L2TAP_SNIFFER_ETH_TYPE_ETHERCAT },
};

config.interface_name = "ETH_DEF";

config.filters = filters;
config.filter_count = sizeof(filters) / sizeof(filters[0]);

config.runtime.max_frame_len = 1600;
config.runtime.ring_buffer_size = 16384;
config.runtime.stats_period_ms = 5000;

config.parser.parse_arp = true;
config.parser.parse_ipv4 = true;
config.parser.parse_transport = true;
config.parser.detect_industrial_protocols = true;
config.parser.payload_preview_bytes = 32;

config.eth.power_gpio = 12;
config.eth.mdc_gpio = 23;
config.eth.mdio_gpio = 18;
config.eth.phy_addr = 0;
config.eth.rmii_clk_gpio = 0;
config.eth.phy_reset_gpio = -1;
config.eth.power_up_delay_ms = 100;
config.eth.link_timeout_ms = 15000;
config.eth.phy = L2TAP_SNIFFER_PHY_RTL8201;

config.callbacks.on_raw_frame = on_raw_frame;
config.callbacks.on_parsed_frame = on_parsed_frame;
config.callbacks.on_event = on_event;
config.callbacks.on_error = on_error;
config.callbacks.user_ctx = NULL;
```

### Como configurar os filtros

Os filtros dizem quais EtherTypes a biblioteca vai capturar em `/dev/net/tap`.

Exemplo:

```c
static const l2tap_sniffer_filter_t filters[] = {
    { "ipv4", L2TAP_SNIFFER_ETH_TYPE_IPV4 },
    { "arp", L2TAP_SNIFFER_ETH_TYPE_ARP },
    { "meu_proto", 0x88B5 },
};

config.filters = filters;
config.filter_count = 3;
```

Boas práticas:

- use `label` curto e estável
- `label` aparece em `raw_frame->capture_label`
- `filter_count` precisa corresponder exatamente ao tamanho do vetor
- a quantidade de filtros não pode passar de `CONFIG_ESP_NETIF_L2_TAP_MAX_FDS`

### Como configurar o parser

O bloco `parser` controla quanto a biblioteca tenta interpretar cada quadro.

Exemplo:

```c
config.parser.parse_arp = true;
config.parser.parse_ipv4 = true;
config.parser.parse_transport = true;
config.parser.detect_industrial_protocols = true;
config.parser.payload_preview_bytes = 32;
```

Interpretação prática:

- `parse_arp = true`
  A biblioteca preenche os campos ARP quando o EtherType for ARP.
- `parse_ipv4 = true`
  A biblioteca interpreta cabeçalhos IPv4.
- `parse_transport = true`
  A biblioteca tenta interpretar TCP e UDP.
- `detect_industrial_protocols = true`
  A biblioteca tenta identificar protocolos industriais conhecidos.
- `payload_preview_bytes = 32`
  Os primeiros 32 bytes do payload serão convertidos para hexadecimal.

Exemplo de parser mais “leve”:

```c
config.parser.parse_arp = false;
config.parser.parse_ipv4 = true;
config.parser.parse_transport = false;
config.parser.detect_industrial_protocols = false;
config.parser.payload_preview_bytes = 16;
```

Esse modo pode ser útil quando você quer:

- reduzir interpretação
- usar sua própria lógica de análise
- trabalhar com callbacks de frame bruto

### Como configurar o runtime

O bloco `runtime` ajusta buffers e temporização interna.

Exemplo:

```c
config.runtime.max_frame_len = 1600;
config.runtime.ring_buffer_size = 16384;
config.runtime.stats_period_ms = 5000;
```

Como pensar nesses parâmetros:

- `max_frame_len`
  Define o tamanho do buffer de recepção usado pelas tasks de captura.
  Se você capturar quadros maiores que esse limite, eles podem ser truncados ou não lidos corretamente.
- `ring_buffer_size`
  Define quanto tráfego pode ficar em fila entre captura e análise.
  Tráfego alto com buffer pequeno tende a aumentar `ring_drops`.
- `stats_period_ms`
  Define o intervalo do log periódico de estatísticas.
  Se não quiser esse log, pode experimentar `0`.

Exemplo de runtime mais conservador:

```c
config.runtime.max_frame_len = 2048;
config.runtime.ring_buffer_size = 32768;
config.runtime.stats_period_ms = 2000;
```

### Como configurar o backend Ethernet

O bloco `eth` define como a biblioteca vai subir a interface Ethernet.

Exemplo para a T-ETH-Lite:

```c
config.eth.power_gpio = 12;
config.eth.mdc_gpio = 23;
config.eth.mdio_gpio = 18;
config.eth.phy_addr = 0;
config.eth.rmii_clk_gpio = 0;
config.eth.phy_reset_gpio = -1;
config.eth.power_up_delay_ms = 100;
config.eth.link_timeout_ms = 15000;
config.eth.phy = L2TAP_SNIFFER_PHY_RTL8201;
```

Significado prático:

- `power_gpio`
  GPIO que liga ou habilita o PHY.
- `mdc_gpio` e `mdio_gpio`
  Linhas de controle do barramento MDIO.
- `phy_addr`
  Endereço do PHY.
- `rmii_clk_gpio`
  GPIO do clock RMII.
- `phy_reset_gpio`
  GPIO de reset do PHY. Use `-1` se o reset não for controlado pela aplicação.
- `power_up_delay_ms`
  Tempo de espera após energizar o PHY.
- `link_timeout_ms`
  Tempo máximo para o link subir.
- `phy`
  Modelo de PHY suportado pela biblioteca.

Importante:

- hoje a implementação real foi validada para `RTL8201`
- a biblioteca ainda não tem backends alternativos para outros tipos de hardware Ethernet

### Como configurar os callbacks

Os callbacks são a forma principal de integrar a biblioteca à sua aplicação.

Exemplo:

```c
config.callbacks.on_raw_frame = on_raw_frame;
config.callbacks.on_parsed_frame = on_parsed_frame;
config.callbacks.on_event = on_event;
config.callbacks.on_error = on_error;
config.callbacks.user_ctx = meu_contexto;
```

Quando usar cada um:

- `on_raw_frame`
  Use quando você quer acesso aos bytes brutos do quadro.
- `on_parsed_frame`
  Use quando você quer trabalhar com campos já interpretados.
- `on_event`
  Use para acompanhar subida de Ethernet, link, IP e início da captura.
- `on_error`
  Use para integrar logs, tratamento de erro ou telemetria.
- `user_ctx`
  Use para passar contexto da sua aplicação para todos os callbacks.

Exemplo de callback de erro:

```c
static void on_error(l2tap_sniffer_handle_t handle,
                     esp_err_t err,
                     const char *message,
                     void *user_ctx)
{
    (void)handle;
    (void)user_ctx;

    printf("erro=%s msg=%s\n", esp_err_to_name(err), message);
}
```

Exemplo de callback de evento:

```c
static void on_event(l2tap_sniffer_handle_t handle,
                     l2tap_sniffer_event_t event,
                     void *user_ctx)
{
    (void)handle;
    (void)user_ctx;

    if (event == L2TAP_SNIFFER_EVENT_CAPTURE_STARTED) {
        printf("captura iniciada\n");
    }
}
```

### Como combinar tudo

Na prática, você normalmente faz isso:

1. cria `config` com `l2tap_sniffer_config_default()`
2. define o vetor de filtros
3. ajusta o bloco `eth` para a placa
4. ajusta parser e runtime se necessário
5. registra callbacks
6. chama `create()` e `start()`

Exemplo resumido:

```c
l2tap_sniffer_config_t config = l2tap_sniffer_config_default();

config.filters = filters;
config.filter_count = ARRAY_SIZE(filters);

config.eth.power_gpio = 12;
config.eth.mdc_gpio = 23;
config.eth.mdio_gpio = 18;
config.eth.phy_addr = 0;
config.eth.rmii_clk_gpio = 0;
config.eth.phy_reset_gpio = -1;
config.eth.phy = L2TAP_SNIFFER_PHY_RTL8201;

config.parser.payload_preview_bytes = 32;
config.callbacks.on_parsed_frame = on_frame;

ESP_ERROR_CHECK(l2tap_sniffer_create(&config, &sniffer));
ESP_ERROR_CHECK(l2tap_sniffer_start(sniffer));
```

### 3. Crie a instância

```c
l2tap_sniffer_handle_t sniffer = NULL;
ESP_ERROR_CHECK(l2tap_sniffer_create(&config, &sniffer));
```

### 4. Inicie a captura

```c
ESP_ERROR_CHECK(l2tap_sniffer_start(sniffer));
```

### 5. Quando quiser encerrar

```c
ESP_ERROR_CHECK(l2tap_sniffer_stop(sniffer));
l2tap_sniffer_destroy(sniffer);
```

## Exemplo Completo de Integração

```c
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_vfs_l2tap.h"
#include "l2tap_sniffer.h"
#include "nvs_flash.h"

static void on_frame(l2tap_sniffer_handle_t handle,
                     const l2tap_sniffer_raw_frame_t *raw_frame,
                     const l2tap_sniffer_parsed_frame_t *parsed_frame,
                     void *user_ctx)
{
    (void)handle;
    (void)user_ctx;

    printf("capture=%s len=%u ethertype=0x%04x src=%s dst=%s\n",
           raw_frame->capture_label,
           raw_frame->frame_len,
           parsed_frame->ethertype,
           parsed_frame->src_mac,
           parsed_frame->dst_mac);
}

void app_main(void)
{
    static const l2tap_sniffer_filter_t filters[] = {
        { "ipv4", L2TAP_SNIFFER_ETH_TYPE_IPV4 },
        { "arp", L2TAP_SNIFFER_ETH_TYPE_ARP },
        { "vlan", L2TAP_SNIFFER_ETH_TYPE_VLAN },
    };

    l2tap_sniffer_handle_t sniffer = NULL;
    l2tap_sniffer_config_t config = l2tap_sniffer_config_default();

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(esp_vfs_l2tap_intf_register(NULL));

    config.filters = filters;
    config.filter_count = 3;

    config.eth.power_gpio = 12;
    config.eth.mdc_gpio = 23;
    config.eth.mdio_gpio = 18;
    config.eth.phy_addr = 0;
    config.eth.rmii_clk_gpio = 0;
    config.eth.phy_reset_gpio = -1;
    config.eth.phy = L2TAP_SNIFFER_PHY_RTL8201;

    config.callbacks.on_parsed_frame = on_frame;

    ESP_ERROR_CHECK(l2tap_sniffer_create(&config, &sniffer));
    ESP_ERROR_CHECK(l2tap_sniffer_start(sniffer));
}
```

## API Pública

### `l2tap_sniffer_runtime_config_default()`

Retorna a configuração padrão de runtime.

### `l2tap_sniffer_parser_config_default()`

Retorna a configuração padrão do parser.

### `l2tap_sniffer_esp32_eth_config_default()`

Retorna a configuração padrão do backend Ethernet atual.

### `l2tap_sniffer_config_default()`

Retorna a configuração padrão completa da biblioteca.

### `l2tap_sniffer_create(const l2tap_sniffer_config_t *cfg, l2tap_sniffer_handle_t *out_handle)`

Cria a instância da biblioteca.

Retorna erro se:

- `cfg` for inválido
- não houver filtros
- `filter_count` for maior que `CONFIG_ESP_NETIF_L2_TAP_MAX_FDS`
- algum campo obrigatório estiver ausente
- faltar memória

### `l2tap_sniffer_start(l2tap_sniffer_handle_t handle)`

Inicia:

- backend Ethernet
- espera de link
- descritores L2 TAP
- tasks de captura
- task de análise
- task de estatísticas

### `l2tap_sniffer_stop(l2tap_sniffer_handle_t handle)`

Interrompe a captura e libera recursos de runtime.

### `l2tap_sniffer_destroy(l2tap_sniffer_handle_t handle)`

Destrói a instância. Se ainda estiver ativa, faz o encerramento antes.

## Todos os Tipos e Parâmetros

### `l2tap_sniffer_filter_t`

Define um filtro de captura.

Campos:

- `label`
  Nome lógico do filtro. Aparece em `raw_frame->capture_label`.
- `ethertype`
  EtherType usado no filtro do L2 TAP.

Exemplo:

```c
{ "arp", L2TAP_SNIFFER_ETH_TYPE_ARP }
```

### `l2tap_sniffer_parser_config_t`

Controla o nível de parsing aplicado aos frames.

Campos:

- `parse_arp`
  Se `true`, a biblioteca tenta interpretar quadros ARP.
- `parse_ipv4`
  Se `true`, a biblioteca tenta interpretar quadros IPv4.
- `parse_transport`
  Se `true`, a biblioteca tenta interpretar TCP e UDP quando possível.
- `detect_industrial_protocols`
  Se `true`, ativa a detecção básica de:
  - `Profinet`
  - `EtherCAT`
  - `Modbus TCP`
  - `EtherNet/IP`
- `payload_preview_bytes`
  Quantidade máxima de bytes do payload convertidos em hexadecimal no campo `payload_preview`.

Limites:

- máximo suportado pela API atual: `256`

### `l2tap_sniffer_runtime_config_t`

Controla parâmetros internos do pipeline de captura.

Campos:

- `max_frame_len`
  Tamanho máximo do buffer de recepção por task de captura.
- `ring_buffer_size`
  Tamanho total do ring buffer compartilhado entre captura e análise.
- `stats_period_ms`
  Intervalo, em milissegundos, da task que imprime estatísticas.
  Se for `0`, a biblioteca tenta operar sem logs periódicos.

### `l2tap_sniffer_esp32_eth_config_t`

Controla o backend Ethernet disponível atualmente.

Campos:

- `power_gpio`
  GPIO que energiza ou habilita o PHY.
  Use `-1` para desabilitar esse controle explícito.
- `mdc_gpio`
  GPIO do sinal `MDC`.
- `mdio_gpio`
  GPIO do sinal `MDIO`.
- `phy_addr`
  Endereço do PHY no barramento MDIO.
- `rmii_clk_gpio`
  GPIO do clock RMII.
- `phy_reset_gpio`
  GPIO de reset do PHY.
  Use `-1` se o reset não for controlado pela aplicação.
- `power_up_delay_ms`
  Tempo de espera após energizar o PHY antes de iniciar o driver Ethernet.
- `link_timeout_ms`
  Tempo máximo de espera até o driver iniciar e o link subir.
- `phy`
  Tipo de PHY usado.

### `l2tap_sniffer_callbacks_t`

Conjunto de callbacks fornecidos pela aplicação.

Campos:

- `on_raw_frame`
  Recebe o frame bruto assim que ele sai da fila para análise.
- `on_parsed_frame`
  Recebe o frame bruto e a estrutura parseada.
  Este costuma ser o callback principal.
- `on_event`
  Recebe eventos de ciclo de vida da biblioteca.
- `on_error`
  Recebe erros operacionais com código `esp_err_t` e mensagem textual.
- `user_ctx`
  Ponteiro livre da aplicação, repassado para todos os callbacks.

### `l2tap_sniffer_config_t`

Estrutura principal de configuração.

Campos:

- `interface_name`
  Nome da interface L2 TAP, normalmente `ETH_DEF`.
- `filters`
  Vetor de filtros.
- `filter_count`
  Quantidade de itens em `filters`.
- `runtime`
  Configuração do pipeline interno.
- `parser`
  Configuração do parser.
- `eth`
  Configuração do backend Ethernet atual.
- `callbacks`
  Conjunto de callbacks da aplicação.

## Eventos Públicos

### `L2TAP_SNIFFER_EVENT_ETH_STARTED`

O driver Ethernet foi iniciado.

### `L2TAP_SNIFFER_EVENT_LINK_UP`

O link Ethernet ficou ativo.

### `L2TAP_SNIFFER_EVENT_IP_ACQUIRED`

A interface recebeu endereço IPv4.

Observação:

- a captura L2 não depende de DHCP ou IP para funcionar
- esse evento é informativo

### `L2TAP_SNIFFER_EVENT_CAPTURE_STARTED`

Os descritores L2 TAP e as tasks principais ficaram prontos.

### `L2TAP_SNIFFER_EVENT_STOPPED`

A biblioteca encerrou o runtime e limpou os recursos.

### `L2TAP_SNIFFER_EVENT_ERROR`

Algum erro operacional foi detectado.

## Dados Entregues à Aplicação

### `l2tap_sniffer_raw_frame_t`

Representa o frame bruto capturado.

Campos:

- `capture_label`
  Nome do filtro que capturou o quadro.
- `ts_us`
  Timestamp em microssegundos.
- `source_filter`
  EtherType do filtro que capturou o quadro.
- `frame_len`
  Tamanho do quadro.
- `frame[]`
  Bytes crus do quadro Ethernet.

### `l2tap_sniffer_parsed_frame_t`

Representa o frame já interpretado pela biblioteca.

Principais grupos de campos:

- Ethernet:
  - `src_mac`
  - `dst_mac`
  - `outer_ethertype`
  - `ethertype`
  - `vlan_id`
- ARP:
  - `has_arp`
  - `arp_opcode`
  - `arp_sender_ip`
  - `arp_target_ip`
- IPv4:
  - `has_ipv4`
  - `ip_version`
  - `ip_header_len`
  - `ip_total_len`
  - `ip_fragment_offset`
  - `ip_more_fragments`
  - `ip_proto`
  - `ip_src`
  - `ip_dst`
- Transporte:
  - `has_l4`
  - `transport`
  - `src_port`
  - `dst_port`
  - `tcp_flags`
- Payload:
  - `payload_len`
  - `payload_preview`
- Classificação industrial:
  - `industrial`

### `l2tap_sniffer_stats_t`

Estrutura interna de contadores do runtime.

Campos:

- `captured`
  Quadros lidos com sucesso dos descritores.
- `enqueued`
  Quadros colocados no ring buffer.
- `emitted`
  Quadros parseados e entregues ao callback de frame parseado.
- `ring_drops`
  Quadros descartados por falta de espaço no ring buffer.
- `read_errors`
  Erros de leitura em descritores L2 TAP.
- `parse_errors`
  Quadros que não puderam ser parseados com sucesso.

## EtherTypes Prontos

A API pública já expõe alguns EtherTypes comuns:

- `L2TAP_SNIFFER_ETH_TYPE_IPV4`
- `L2TAP_SNIFFER_ETH_TYPE_ARP`
- `L2TAP_SNIFFER_ETH_TYPE_VLAN`
- `L2TAP_SNIFFER_ETH_TYPE_QINQ`
- `L2TAP_SNIFFER_ETH_TYPE_PROFINET`
- `L2TAP_SNIFFER_ETH_TYPE_ETHERCAT`

Você também pode usar qualquer outro EtherType manualmente:

```c
{ "custom", 0x88B5 }
```

## Comportamento em Caso de Erro

A biblioteca foi desenhada para evitar `abort()` no fluxo normal de uso da API.

Em caso de falha:

- a função retorna `esp_err_t`
- o callback `on_error` pode ser chamado
- o evento `L2TAP_SNIFFER_EVENT_ERROR` pode ser emitido
- recursos parcialmente criados são limpos antes do retorno

## Limitações Atuais

- backend Ethernet atual focado em `ESP32 + EMAC interno + RMII + RTL8201`
- ainda não há backend separado para `ESP32-S2`, `ESP32-S3` ou Ethernet via `SPI`
- a aplicação ainda precisa preparar `NVS`, `esp_netif`, event loop e `esp_vfs_l2tap`

## Estrutura do Projeto

- [components/l2tap_sniffer](c:/Users/CLP2-U001/Documents/l2tap_industrial_sniffer/l2tap/components/l2tap_sniffer): biblioteca reutilizável
- [main](c:/Users/CLP2-U001/Documents/l2tap_industrial_sniffer/l2tap/main): exemplo oficial de uso

## Próximos Passos Recomendados

Se o objetivo for publicar a biblioteca como componente reutilizável no GitHub, os próximos passos mais naturais são:

- criar um `README.md` próprio dentro de `components/l2tap_sniffer`
- adicionar exemplos mínimos de integração
- preparar versionamento semântico
- publicar via GitHub ou ESP Component Registry
- evoluir a arquitetura para múltiplos backends Ethernet
