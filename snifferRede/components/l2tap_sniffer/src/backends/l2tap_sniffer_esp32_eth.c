/*
 * Backend Ethernet baseado no EMAC interno do ESP32.
 * O backend é configurado em tempo de execução pela aplicação consumidora.
 */

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_eth.h"
#include "esp_eth_mac_esp.h"
#include "esp_eth_phy_rtl8201.h"
#include "esp_event.h"
#include "esp_log.h"
#include "l2tap_sniffer_internal.h"

enum {
    L2TAP_SNIFFER_ETH_STARTED_BIT = BIT0,
    L2TAP_SNIFFER_ETH_LINK_UP_BIT = BIT1,
    L2TAP_SNIFFER_ETH_GOT_IP_BIT  = BIT2,
};

static const char *TAG = L2TAP_SNIFFER_TAG;

static esp_err_t enable_eth_power_if_needed(l2tap_sniffer_handle_t handle)
{
    if (handle->config.eth.power_gpio < 0) {
        return ESP_OK;
    }

    gpio_config_t io_conf = {
        .pin_bit_mask = 1ULL << handle->config.eth.power_gpio,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };

    esp_err_t err = gpio_config(&io_conf);
    if (err != ESP_OK) {
        return err;
    }

    err = gpio_set_level(handle->config.eth.power_gpio, 1);
    if (err != ESP_OK) {
        return err;
    }

    vTaskDelay(pdMS_TO_TICKS(handle->config.eth.power_up_delay_ms));
    return ESP_OK;
}

static void eth_event_handler(void *arg, esp_event_base_t event_base, int32_t event_id, void *event_data)
{
    l2tap_sniffer_handle_t handle = (l2tap_sniffer_handle_t)arg;

    (void)event_base;
    (void)event_data;

    if ((handle == NULL) || (handle->eth.event_group == NULL)) {
        return;
    }

    switch (event_id) {
    case ETHERNET_EVENT_START:
        ESP_LOGI(TAG, "Ethernet driver started");
        xEventGroupSetBits(handle->eth.event_group, L2TAP_SNIFFER_ETH_STARTED_BIT);
        l2tap_sniffer_raise_event(handle, L2TAP_SNIFFER_EVENT_ETH_STARTED);
        break;
    case ETHERNET_EVENT_CONNECTED:
        ESP_LOGI(TAG, "Ethernet link up");
        xEventGroupSetBits(handle->eth.event_group, L2TAP_SNIFFER_ETH_LINK_UP_BIT);
        l2tap_sniffer_raise_event(handle, L2TAP_SNIFFER_EVENT_LINK_UP);
        break;
    case ETHERNET_EVENT_DISCONNECTED:
        ESP_LOGW(TAG, "Ethernet link down");
        xEventGroupClearBits(handle->eth.event_group,
                             L2TAP_SNIFFER_ETH_LINK_UP_BIT | L2TAP_SNIFFER_ETH_GOT_IP_BIT);
        break;
    case ETHERNET_EVENT_STOP:
        ESP_LOGI(TAG, "Ethernet driver stopped");
        xEventGroupClearBits(handle->eth.event_group,
                             L2TAP_SNIFFER_ETH_STARTED_BIT |
                             L2TAP_SNIFFER_ETH_LINK_UP_BIT |
                             L2TAP_SNIFFER_ETH_GOT_IP_BIT);
        break;
    default:
        break;
    }
}

static void got_ip_event_handler(void *arg, esp_event_base_t event_base, int32_t event_id, void *event_data)
{
    l2tap_sniffer_handle_t handle = (l2tap_sniffer_handle_t)arg;

    (void)event_base;
    (void)event_id;

    if ((handle == NULL) || (handle->eth.event_group == NULL) || (handle->eth.netif == NULL)) {
        return;
    }

    ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
    if (event->esp_netif != handle->eth.netif) {
        return;
    }

    ESP_LOGI(TAG, "Ethernet got IPv4 address: " IPSTR, IP2STR(&event->ip_info.ip));
    xEventGroupSetBits(handle->eth.event_group, L2TAP_SNIFFER_ETH_GOT_IP_BIT);
    l2tap_sniffer_raise_event(handle, L2TAP_SNIFFER_EVENT_IP_ACQUIRED);
}

void l2tap_sniffer_eth_stop(l2tap_sniffer_handle_t handle)
{
    if (handle == NULL) {
        return;
    }

    if (handle->eth.handle != NULL) {
        (void)esp_eth_stop(handle->eth.handle);
    }

    (void)esp_event_handler_unregister(IP_EVENT, IP_EVENT_ETH_GOT_IP, got_ip_event_handler);
    (void)esp_event_handler_unregister(ETH_EVENT, ESP_EVENT_ANY_ID, eth_event_handler);

    if (handle->eth.glue != NULL) {
        (void)esp_eth_del_netif_glue(handle->eth.glue);
        handle->eth.glue = NULL;
    }

    if (handle->eth.netif != NULL) {
        esp_netif_destroy(handle->eth.netif);
        handle->eth.netif = NULL;
    }

    if (handle->eth.handle != NULL) {
        (void)esp_eth_driver_uninstall(handle->eth.handle);
        handle->eth.handle = NULL;
    }

    if (handle->eth.event_group != NULL) {
        vEventGroupDelete(handle->eth.event_group);
        handle->eth.event_group = NULL;
    }
}

esp_err_t l2tap_sniffer_eth_start(l2tap_sniffer_handle_t handle)
{
    esp_err_t err;
    eth_mac_config_t mac_config = ETH_MAC_DEFAULT_CONFIG();
    eth_phy_config_t phy_config = ETH_PHY_DEFAULT_CONFIG();
    eth_esp32_emac_config_t emac_config = ETH_ESP32_EMAC_DEFAULT_CONFIG();
    esp_eth_mac_t *mac = NULL;
    esp_eth_phy_t *phy = NULL;
    esp_netif_config_t netif_config = ESP_NETIF_DEFAULT_ETH();

    if (handle == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    err = enable_eth_power_if_needed(handle);
    if (err != ESP_OK) {
        return err;
    }

    handle->eth.event_group = xEventGroupCreate();
    if (handle->eth.event_group == NULL) {
        return ESP_ERR_NO_MEM;
    }

    err = esp_event_handler_register(ETH_EVENT, ESP_EVENT_ANY_ID, eth_event_handler, handle);
    if (err != ESP_OK) {
        l2tap_sniffer_eth_stop(handle);
        return err;
    }

    err = esp_event_handler_register(IP_EVENT, IP_EVENT_ETH_GOT_IP, got_ip_event_handler, handle);
    if (err != ESP_OK) {
        l2tap_sniffer_eth_stop(handle);
        return err;
    }

    handle->eth.netif = esp_netif_new(&netif_config);
    if (handle->eth.netif == NULL) {
        l2tap_sniffer_eth_stop(handle);
        return ESP_ERR_NO_MEM;
    }

    mac_config.rx_task_stack_size = 4096;
    emac_config.smi_gpio.mdc_num = handle->config.eth.mdc_gpio;
    emac_config.smi_gpio.mdio_num = handle->config.eth.mdio_gpio;
    emac_config.interface = EMAC_DATA_INTERFACE_RMII;
    emac_config.clock_config.rmii.clock_mode = EMAC_CLK_EXT_IN;
    emac_config.clock_config.rmii.clock_gpio = handle->config.eth.rmii_clk_gpio;

    phy_config.phy_addr = handle->config.eth.phy_addr;
    phy_config.reset_gpio_num = handle->config.eth.phy_reset_gpio;

    mac = esp_eth_mac_new_esp32(&emac_config, &mac_config);
    if (mac == NULL) {
        l2tap_sniffer_eth_stop(handle);
        return ESP_ERR_NO_MEM;
    }

    switch (handle->config.eth.phy) {
    case L2TAP_SNIFFER_PHY_RTL8201:
        phy = esp_eth_phy_new_rtl8201(&phy_config);
        break;
    default:
        mac->del(mac);
        l2tap_sniffer_eth_stop(handle);
        return ESP_ERR_NOT_SUPPORTED;
    }

    if (phy == NULL) {
        mac->del(mac);
        l2tap_sniffer_eth_stop(handle);
        return ESP_ERR_NO_MEM;
    }

    esp_eth_config_t eth_config = ETH_DEFAULT_CONFIG(mac, phy);
    err = esp_eth_driver_install(&eth_config, &handle->eth.handle);
    if (err != ESP_OK) {
        mac->del(mac);
        phy->del(phy);
        l2tap_sniffer_eth_stop(handle);
        return err;
    }

    handle->eth.glue = esp_eth_new_netif_glue(handle->eth.handle);
    if (handle->eth.glue == NULL) {
        l2tap_sniffer_eth_stop(handle);
        return ESP_ERR_NO_MEM;
    }

    err = esp_netif_attach(handle->eth.netif, handle->eth.glue);
    if (err != ESP_OK) {
        l2tap_sniffer_eth_stop(handle);
        return err;
    }

    err = esp_eth_start(handle->eth.handle);
    if (err != ESP_OK) {
        l2tap_sniffer_eth_stop(handle);
        return err;
    }

    ESP_LOGI(TAG,
             "Starting Ethernet backend: phy=RTL8201 mdc=%d mdio=%d phy_addr=%d rmii_clk_gpio=%d power_gpio=%d",
             handle->config.eth.mdc_gpio,
             handle->config.eth.mdio_gpio,
             handle->config.eth.phy_addr,
             handle->config.eth.rmii_clk_gpio,
             handle->config.eth.power_gpio);
    return ESP_OK;
}

esp_err_t l2tap_sniffer_eth_wait_ready(l2tap_sniffer_handle_t handle, uint32_t timeout_ms)
{
    EventBits_t bits;

    if ((handle == NULL) || (handle->eth.event_group == NULL)) {
        return ESP_ERR_INVALID_STATE;
    }

    bits = xEventGroupWaitBits(handle->eth.event_group,
                               L2TAP_SNIFFER_ETH_STARTED_BIT | L2TAP_SNIFFER_ETH_LINK_UP_BIT,
                               pdFALSE,
                               pdTRUE,
                               pdMS_TO_TICKS(timeout_ms));

    if ((bits & (L2TAP_SNIFFER_ETH_STARTED_BIT | L2TAP_SNIFFER_ETH_LINK_UP_BIT)) !=
        (L2TAP_SNIFFER_ETH_STARTED_BIT | L2TAP_SNIFFER_ETH_LINK_UP_BIT)) {
        return ESP_ERR_TIMEOUT;
    }

    bits = xEventGroupGetBits(handle->eth.event_group);
    if ((bits & L2TAP_SNIFFER_ETH_GOT_IP_BIT) == 0) {
        ESP_LOGW(TAG, "Ethernet link is up but no IPv4 address was acquired yet");
    }

    return ESP_OK;
}
