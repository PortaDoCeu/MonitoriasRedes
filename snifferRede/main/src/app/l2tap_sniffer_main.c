/*
 * SPDX-FileCopyrightText: 2026 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Unlicense OR CC0-1.0
 */

#include <stdio.h>
#include "sdkconfig.h"
#include "esp_err.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_vfs_l2tap.h"
#include "l2tap_sniffer.h"
#include "nvs_flash.h"
#include "sniffer_output.h"

#ifndef CONFIG_EXAMPLE_SNIFFER_PAYLOAD_PREVIEW_BYTES
#define CONFIG_EXAMPLE_SNIFFER_PAYLOAD_PREVIEW_BYTES 32
#endif

#ifndef CONFIG_EXAMPLE_SNIFFER_MAX_FRAME_LEN
#define CONFIG_EXAMPLE_SNIFFER_MAX_FRAME_LEN 1600
#endif

#ifndef CONFIG_EXAMPLE_SNIFFER_STATS_PERIOD_MS
#define CONFIG_EXAMPLE_SNIFFER_STATS_PERIOD_MS 5000
#endif

#ifndef CONFIG_EXAMPLE_SNIFFER_RING_BUFFER_SIZE
#define CONFIG_EXAMPLE_SNIFFER_RING_BUFFER_SIZE 16384
#endif

#ifndef CONFIG_EXAMPLE_SNIFFER_ETH_POWER_GPIO
#define CONFIG_EXAMPLE_SNIFFER_ETH_POWER_GPIO 12
#endif

#ifndef CONFIG_EXAMPLE_SNIFFER_ETH_POWER_UP_DELAY_MS
#define CONFIG_EXAMPLE_SNIFFER_ETH_POWER_UP_DELAY_MS 100
#endif

#ifndef CONFIG_EXAMPLE_SNIFFER_ETH_LINK_UP_TIMEOUT_MS
#define CONFIG_EXAMPLE_SNIFFER_ETH_LINK_UP_TIMEOUT_MS 15000
#endif

#define EXAMPLE_TAG               "l2tap_sniffer"
#define T_ETH_LITE_MDC_GPIO       23
#define T_ETH_LITE_MDIO_GPIO      18
#define T_ETH_LITE_PHY_ADDR       0
#define T_ETH_LITE_RMII_CLK_GPIO  0
#define T_ETH_LITE_PHY_RESET_GPIO -1
#define ARRAY_SIZE(x)             (sizeof(x) / sizeof((x)[0]))

static const char *TAG = EXAMPLE_TAG;
static l2tap_sniffer_handle_t s_sniffer;

static const l2tap_sniffer_filter_t s_filters[] = {
    { "ipv4", L2TAP_SNIFFER_ETH_TYPE_IPV4 },
    { "arp", L2TAP_SNIFFER_ETH_TYPE_ARP },
    { "vlan", L2TAP_SNIFFER_ETH_TYPE_VLAN },
    { "qinq", L2TAP_SNIFFER_ETH_TYPE_QINQ },
    { "profinet", L2TAP_SNIFFER_ETH_TYPE_PROFINET },
    { "ethercat", L2TAP_SNIFFER_ETH_TYPE_ETHERCAT },
};

/*
 * Inicializa a NVS, que é a área de armazenamento persistente do ESP32.
 *
 * A NVS guarda dados internos do sistema e configurações que precisam
 * sobreviver a reinicializações. Quando a estrutura salva fica incompatível
 * com a versão atual do firmware, limpamos a área e reconstruímos a NVS.
 */
static esp_err_t init_nvs(void)
{
    esp_err_t ret = nvs_flash_init();

    if ((ret == ESP_ERR_NVS_NO_FREE_PAGES) || (ret == ESP_ERR_NVS_NEW_VERSION_FOUND)) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }

    return ret;
}

/*
 * O callback de frames parseados é o ponto em que o exemplo transforma
 * a biblioteca em uma aplicação concreta. Aqui escolhemos serializar tudo
 * como JSON para a UART, mas outra aplicação poderia salvar em arquivo,
 * enviar por rede ou alimentar uma interface gráfica.
 */
static void on_parsed_frame(l2tap_sniffer_handle_t handle,
                            const l2tap_sniffer_raw_frame_t *raw_frame,
                            const l2tap_sniffer_parsed_frame_t *parsed_frame,
                            void *user_ctx)
{
    (void)handle;
    (void)user_ctx;

    sniffer_output_emit_json(raw_frame, parsed_frame);
}

/*
 * Este callback ilustra como a aplicação pode reagir aos eventos da biblioteca
 * sem conhecer os detalhes internos do backend Ethernet ou das tasks de captura.
 */
static void on_sniffer_event(l2tap_sniffer_handle_t handle, l2tap_sniffer_event_t event, void *user_ctx)
{
    (void)handle;
    (void)user_ctx;

    switch (event) {
    case L2TAP_SNIFFER_EVENT_CAPTURE_STARTED:
        ESP_LOGI(TAG, "Capture pipeline reported as ready by the library");
        break;
    case L2TAP_SNIFFER_EVENT_STOPPED:
        ESP_LOGI(TAG, "Sniffer library stopped");
        break;
    default:
        break;
    }
}

/*
 * app_main() funciona como exemplo oficial de uso da biblioteca.
 *
 * O objetivo aqui é mostrar a sequência mínima de integração:
 * 1. preparar os serviços básicos do ESP-IDF;
 * 2. montar uma configuração da biblioteca para a T-ETH-Lite;
 * 3. registrar callbacks;
 * 4. criar e iniciar o sniffer reutilizável.
 */
void app_main(void)
{
    esp_err_t err;
    l2tap_sniffer_config_t config = l2tap_sniffer_config_default();

    /*
     * Mantém a saída JSON sem buffer para que cada frame apareça
     * imediatamente no monitor serial.
     */
    setvbuf(stdout, NULL, _IONBF, 0);

    /*
     * Estes serviços do ESP-IDF continuam sendo responsabilidade da aplicação
     * hospedeira. A biblioteca assume que o ambiente de rede e o VFS L2 TAP
     * já foram preparados antes do start.
     */
    ESP_ERROR_CHECK(init_nvs());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(esp_vfs_l2tap_intf_register(NULL));

    config.filters = s_filters;
    config.filter_count = ARRAY_SIZE(s_filters);
    config.runtime.max_frame_len = CONFIG_EXAMPLE_SNIFFER_MAX_FRAME_LEN;
    config.runtime.ring_buffer_size = CONFIG_EXAMPLE_SNIFFER_RING_BUFFER_SIZE;
    config.runtime.stats_period_ms = CONFIG_EXAMPLE_SNIFFER_STATS_PERIOD_MS;
    config.parser.payload_preview_bytes = CONFIG_EXAMPLE_SNIFFER_PAYLOAD_PREVIEW_BYTES;
    config.eth.power_gpio = CONFIG_EXAMPLE_SNIFFER_ETH_POWER_GPIO;
    config.eth.mdc_gpio = T_ETH_LITE_MDC_GPIO;
    config.eth.mdio_gpio = T_ETH_LITE_MDIO_GPIO;
    config.eth.phy_addr = T_ETH_LITE_PHY_ADDR;
    config.eth.rmii_clk_gpio = T_ETH_LITE_RMII_CLK_GPIO;
    config.eth.phy_reset_gpio = T_ETH_LITE_PHY_RESET_GPIO;
    config.eth.power_up_delay_ms = CONFIG_EXAMPLE_SNIFFER_ETH_POWER_UP_DELAY_MS;
    config.eth.link_timeout_ms = CONFIG_EXAMPLE_SNIFFER_ETH_LINK_UP_TIMEOUT_MS;
    config.callbacks.on_parsed_frame = on_parsed_frame;
    config.callbacks.on_event = on_sniffer_event;

    ESP_LOGI(TAG, "Industrial filters active: IPv4, ARP, VLAN, QinQ, Profinet, EtherCAT");
    ESP_LOGI(TAG, "JSON output enabled on UART, payload preview=%d bytes",
             CONFIG_EXAMPLE_SNIFFER_PAYLOAD_PREVIEW_BYTES);

    err = l2tap_sniffer_create(&config, &s_sniffer);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Unable to create sniffer handle: %s", esp_err_to_name(err));
        return;
    }

    err = l2tap_sniffer_start(s_sniffer);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Unable to start sniffer library: %s", esp_err_to_name(err));
        l2tap_sniffer_destroy(s_sniffer);
        s_sniffer = NULL;
        return;
    }
}
