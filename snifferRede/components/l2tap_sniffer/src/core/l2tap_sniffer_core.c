/*
 * Núcleo da biblioteca l2tap_sniffer.
 * Este módulo coordena validação, captura, callbacks, estatísticas e ciclo de vida.
 */

#include <errno.h>
#include <inttypes.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/fcntl.h>
#include <sys/ioctl.h>
#include "esp_log.h"
#include "esp_timer.h"
#include "esp_vfs_l2tap.h"
#include "l2tap_sniffer_internal.h"

static const char *TAG = L2TAP_SNIFFER_TAG;

static void stats_increment(uint32_t *counter, l2tap_sniffer_handle_t handle)
{
    portENTER_CRITICAL(&handle->stats_lock);
    (*counter)++;
    portEXIT_CRITICAL(&handle->stats_lock);
}

static void stats_snapshot(l2tap_sniffer_handle_t handle, l2tap_sniffer_stats_t *snapshot)
{
    portENTER_CRITICAL(&handle->stats_lock);
    *snapshot = handle->stats;
    portEXIT_CRITICAL(&handle->stats_lock);
}

void l2tap_sniffer_raise_event(l2tap_sniffer_handle_t handle, l2tap_sniffer_event_t event)
{
    if ((handle != NULL) && (handle->config.callbacks.on_event != NULL)) {
        handle->config.callbacks.on_event(handle, event, handle->config.callbacks.user_ctx);
    }
}

void l2tap_sniffer_report_error(l2tap_sniffer_handle_t handle, esp_err_t err, const char *fmt, ...)
{
    char message[192];
    va_list args;

    va_start(args, fmt);
    vsnprintf(message, sizeof(message), fmt, args);
    va_end(args);

    ESP_LOGE(TAG, "%s: %s", esp_err_to_name(err), message);

    if ((handle != NULL) && (handle->config.callbacks.on_error != NULL)) {
        handle->config.callbacks.on_error(handle, err, message, handle->config.callbacks.user_ctx);
    }

    l2tap_sniffer_raise_event(handle, L2TAP_SNIFFER_EVENT_ERROR);
}

static bool tasks_are_stopped(l2tap_sniffer_handle_t handle)
{
    if ((handle->analyzer_task != NULL) || (handle->stats_task != NULL)) {
        return false;
    }

    for (size_t i = 0; i < handle->config.filter_count; ++i) {
        if (handle->sources[i].task_handle != NULL) {
            return false;
        }
    }

    return true;
}

static void force_delete_remaining_tasks(l2tap_sniffer_handle_t handle)
{
    if (handle->analyzer_task != NULL) {
        vTaskDelete(handle->analyzer_task);
        handle->analyzer_task = NULL;
    }

    if (handle->stats_task != NULL) {
        vTaskDelete(handle->stats_task);
        handle->stats_task = NULL;
    }

    for (size_t i = 0; i < handle->config.filter_count; ++i) {
        if (handle->sources[i].task_handle != NULL) {
            vTaskDelete(handle->sources[i].task_handle);
            handle->sources[i].task_handle = NULL;
        }
    }
}

static void close_capture_sources(l2tap_sniffer_handle_t handle)
{
    for (size_t i = 0; i < handle->config.filter_count; ++i) {
        if (handle->sources[i].fd != L2TAP_SNIFFER_INVALID_FD) {
            close(handle->sources[i].fd);
            handle->sources[i].fd = L2TAP_SNIFFER_INVALID_FD;
        }
    }
}

static void wait_for_tasks_to_finish(l2tap_sniffer_handle_t handle)
{
    TickType_t deadline = xTaskGetTickCount() + pdMS_TO_TICKS(L2TAP_SNIFFER_TASK_JOIN_WAIT_MS);

    while (!tasks_are_stopped(handle) && (xTaskGetTickCount() < deadline)) {
        vTaskDelay(pdMS_TO_TICKS(20));
    }

    if (!tasks_are_stopped(handle)) {
        force_delete_remaining_tasks(handle);
    }
}

static void runtime_cleanup(l2tap_sniffer_handle_t handle, bool emit_event)
{
    bool had_activity = handle->started || handle->running ||
                        (handle->capture_ring != NULL) || (handle->eth.handle != NULL);

    handle->running = false;
    close_capture_sources(handle);

    if (handle->stats_task != NULL) {
        xTaskAbortDelay(handle->stats_task);
    }

    wait_for_tasks_to_finish(handle);

    if (handle->capture_ring != NULL) {
        vRingbufferDelete(handle->capture_ring);
        handle->capture_ring = NULL;
    }

    l2tap_sniffer_eth_stop(handle);
    handle->started = false;

    if (emit_event && had_activity) {
        l2tap_sniffer_raise_event(handle, L2TAP_SNIFFER_EVENT_STOPPED);
    }
}

static esp_err_t validate_config(const l2tap_sniffer_config_t *config)
{
    if ((config == NULL) || (config->filters == NULL) || (config->filter_count == 0)) {
        return ESP_ERR_INVALID_ARG;
    }

    if (config->filter_count > CONFIG_ESP_NETIF_L2_TAP_MAX_FDS) {
        return ESP_ERR_INVALID_ARG;
    }

    if (config->parser.payload_preview_bytes > L2TAP_SNIFFER_MAX_PAYLOAD_PREVIEW_BYTES) {
        return ESP_ERR_INVALID_ARG;
    }

    for (size_t i = 0; i < config->filter_count; ++i) {
        if ((config->filters[i].label == NULL) || (config->filters[i].label[0] == '\0')) {
            return ESP_ERR_INVALID_ARG;
        }
    }

    return ESP_OK;
}

static void normalize_config(l2tap_sniffer_config_t *dst, const l2tap_sniffer_config_t *src)
{
    *dst = *src;

    if (dst->interface_name == NULL) {
        dst->interface_name = L2TAP_SNIFFER_DEFAULT_INTERFACE_NAME;
    }

    if (dst->runtime.max_frame_len == 0) {
        dst->runtime.max_frame_len = CONFIG_EXAMPLE_SNIFFER_MAX_FRAME_LEN;
    }

    if (dst->runtime.ring_buffer_size == 0) {
        dst->runtime.ring_buffer_size = CONFIG_EXAMPLE_SNIFFER_RING_BUFFER_SIZE;
    }

    if (dst->parser.payload_preview_bytes == 0) {
        dst->parser.payload_preview_bytes = CONFIG_EXAMPLE_SNIFFER_PAYLOAD_PREVIEW_BYTES;
    }

    if (dst->eth.power_up_delay_ms == 0) {
        dst->eth.power_up_delay_ms = CONFIG_EXAMPLE_SNIFFER_ETH_POWER_UP_DELAY_MS;
    }

    if (dst->eth.link_timeout_ms == 0) {
        dst->eth.link_timeout_ms = CONFIG_EXAMPLE_SNIFFER_ETH_LINK_UP_TIMEOUT_MS;
    }
}

static void fill_capture_label(char out[L2TAP_SNIFFER_CAPTURE_LABEL_LEN], const char *label)
{
    snprintf(out, L2TAP_SNIFFER_CAPTURE_LABEL_LEN, "%s", label);
}

static void log_local_mac(int fd)
{
    esp_eth_handle_t eth_handle = NULL;
    uint8_t mac[L2TAP_SNIFFER_MAC_ADDR_LEN];

    if (ioctl(fd, L2TAP_G_DEVICE_DRV_HNDL, &eth_handle) < 0) {
        ESP_LOGE(TAG, "Unable to query Ethernet driver handle from fd %d: errno %d", fd, errno);
        return;
    }

    if (esp_eth_ioctl(eth_handle, ETH_CMD_G_MAC_ADDR, mac) != ESP_OK) {
        ESP_LOGE(TAG, "Unable to read Ethernet MAC address from driver");
        return;
    }

    ESP_LOGI(TAG, "Ethernet HW Addr %02x:%02x:%02x:%02x:%02x:%02x",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

static int open_l2tap_fd(l2tap_sniffer_handle_t handle, l2tap_sniffer_capture_source_t *source)
{
    errno = 0;
    int fd = open("/dev/net/tap", O_RDONLY);

    if (fd < 0) {
        l2tap_sniffer_report_error(handle,
                                   ESP_FAIL,
                                   "Unable to open L2 TAP for %s: errno %d (max_fds=%d configured_filters=%u)",
                                   source->label,
                                   errno,
                                   CONFIG_ESP_NETIF_L2_TAP_MAX_FDS,
                                   (unsigned)handle->config.filter_count);
        return L2TAP_SNIFFER_INVALID_FD;
    }

    if (ioctl(fd, L2TAP_S_INTF_DEVICE, handle->config.interface_name) < 0) {
        l2tap_sniffer_report_error(handle,
                                   ESP_FAIL,
                                   "Unable to bind fd %d to %s for %s: errno %d",
                                   fd,
                                   handle->config.interface_name,
                                   source->label,
                                   errno);
        close(fd);
        return L2TAP_SNIFFER_INVALID_FD;
    }

    if (ioctl(fd, L2TAP_S_RCV_FILTER, &source->ethertype) < 0) {
        l2tap_sniffer_report_error(handle,
                                   ESP_FAIL,
                                   "Unable to set filter 0x%04x for %s: errno %d",
                                   source->ethertype,
                                   source->label,
                                   errno);
        close(fd);
        return L2TAP_SNIFFER_INVALID_FD;
    }

    ESP_LOGI(TAG, "fd %d bound to %s with EtherType filter 0x%04x (%s)",
             fd, handle->config.interface_name, source->ethertype, source->label);
    return fd;
}

static void capture_task(void *pv_parameters)
{
    l2tap_sniffer_capture_source_t *source = (l2tap_sniffer_capture_source_t *)pv_parameters;
    l2tap_sniffer_handle_t handle = source->owner;
    uint8_t *rx_buffer = malloc(handle->config.runtime.max_frame_len);

    if (rx_buffer == NULL) {
        l2tap_sniffer_report_error(handle, ESP_ERR_NO_MEM, "Unable to allocate RX buffer for %s", source->label);
        source->task_handle = NULL;
        vTaskDelete(NULL);
        return;
    }

    while (handle->running) {
        ssize_t len = read(source->fd, rx_buffer, handle->config.runtime.max_frame_len);

        if (len < 0) {
            if (errno == EINTR) {
                continue;
            }

            if (!handle->running) {
                break;
            }

            stats_increment(&handle->stats.read_errors, handle);
            ESP_LOGW(TAG, "read() failed on %s fd %d: errno %d", source->label, source->fd, errno);
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        if (len == 0) {
            continue;
        }

        stats_increment(&handle->stats.captured, handle);

        size_t item_size = sizeof(l2tap_sniffer_raw_frame_t) + (size_t)len;
        l2tap_sniffer_raw_frame_t *captured = NULL;

        if (xRingbufferSendAcquire(handle->capture_ring, (void **)&captured, item_size, 0) != pdTRUE) {
            stats_increment(&handle->stats.ring_drops, handle);
            continue;
        }

        fill_capture_label(captured->capture_label, source->label);
        captured->ts_us = esp_timer_get_time();
        captured->source_filter = source->ethertype;
        captured->frame_len = (uint16_t)len;
        memcpy(captured->frame, rx_buffer, (size_t)len);

        xRingbufferSendComplete(handle->capture_ring, captured);
        stats_increment(&handle->stats.enqueued, handle);
    }

    free(rx_buffer);
    source->task_handle = NULL;
    vTaskDelete(NULL);
}

static void analyzer_task(void *pv_parameters)
{
    l2tap_sniffer_handle_t handle = (l2tap_sniffer_handle_t)pv_parameters;

    while (handle->running) {
        size_t item_size = 0;
        l2tap_sniffer_raw_frame_t *captured = (l2tap_sniffer_raw_frame_t *)xRingbufferReceive(
            handle->capture_ring,
            &item_size,
            pdMS_TO_TICKS(L2TAP_SNIFFER_ANALYZER_WAIT_MS));

        if (captured == NULL) {
            continue;
        }

        if (handle->config.callbacks.on_raw_frame != NULL) {
            handle->config.callbacks.on_raw_frame(handle, captured, handle->config.callbacks.user_ctx);
        }

        l2tap_sniffer_parsed_frame_t parsed;

        if (l2tap_sniffer_parse_frame_internal(&handle->config.parser, captured, &parsed)) {
            if (handle->config.callbacks.on_parsed_frame != NULL) {
                handle->config.callbacks.on_parsed_frame(handle, captured, &parsed, handle->config.callbacks.user_ctx);
            }
            stats_increment(&handle->stats.emitted, handle);
        } else {
            stats_increment(&handle->stats.parse_errors, handle);
        }

        vRingbufferReturnItem(handle->capture_ring, captured);
    }

    handle->analyzer_task = NULL;
    vTaskDelete(NULL);
}

static void stats_task(void *pv_parameters)
{
    l2tap_sniffer_handle_t handle = (l2tap_sniffer_handle_t)pv_parameters;

    while (handle->running) {
        l2tap_sniffer_stats_t snapshot;

        vTaskDelay(pdMS_TO_TICKS(handle->config.runtime.stats_period_ms));
        if (!handle->running) {
            break;
        }

        stats_snapshot(handle, &snapshot);
        ESP_LOGI(TAG,
                 "stats captured=%" PRIu32 " enqueued=%" PRIu32 " emitted=%" PRIu32
                 " ring_drops=%" PRIu32 " read_errors=%" PRIu32 " parse_errors=%" PRIu32,
                 snapshot.captured,
                 snapshot.enqueued,
                 snapshot.emitted,
                 snapshot.ring_drops,
                 snapshot.read_errors,
                 snapshot.parse_errors);
    }

    handle->stats_task = NULL;
    vTaskDelete(NULL);
}

l2tap_sniffer_runtime_config_t l2tap_sniffer_runtime_config_default(void)
{
    l2tap_sniffer_runtime_config_t config = {
        .max_frame_len = CONFIG_EXAMPLE_SNIFFER_MAX_FRAME_LEN,
        .ring_buffer_size = CONFIG_EXAMPLE_SNIFFER_RING_BUFFER_SIZE,
        .stats_period_ms = CONFIG_EXAMPLE_SNIFFER_STATS_PERIOD_MS,
    };

    return config;
}

l2tap_sniffer_parser_config_t l2tap_sniffer_parser_config_default(void)
{
    l2tap_sniffer_parser_config_t config = {
        .parse_arp = true,
        .parse_ipv4 = true,
        .parse_transport = true,
        .detect_industrial_protocols = true,
        .payload_preview_bytes = CONFIG_EXAMPLE_SNIFFER_PAYLOAD_PREVIEW_BYTES,
    };

    return config;
}

l2tap_sniffer_esp32_eth_config_t l2tap_sniffer_esp32_eth_config_default(void)
{
    l2tap_sniffer_esp32_eth_config_t config = {
        .power_gpio = -1,
        .mdc_gpio = -1,
        .mdio_gpio = -1,
        .phy_addr = 0,
        .rmii_clk_gpio = -1,
        .phy_reset_gpio = -1,
        .power_up_delay_ms = CONFIG_EXAMPLE_SNIFFER_ETH_POWER_UP_DELAY_MS,
        .link_timeout_ms = CONFIG_EXAMPLE_SNIFFER_ETH_LINK_UP_TIMEOUT_MS,
        .phy = L2TAP_SNIFFER_PHY_RTL8201,
    };

    return config;
}

l2tap_sniffer_config_t l2tap_sniffer_config_default(void)
{
    l2tap_sniffer_config_t config = {
        .interface_name = L2TAP_SNIFFER_DEFAULT_INTERFACE_NAME,
        .filters = NULL,
        .filter_count = 0,
        .runtime = l2tap_sniffer_runtime_config_default(),
        .parser = l2tap_sniffer_parser_config_default(),
        .eth = l2tap_sniffer_esp32_eth_config_default(),
        .callbacks = { 0 },
    };

    return config;
}

esp_err_t l2tap_sniffer_create(const l2tap_sniffer_config_t *cfg, l2tap_sniffer_handle_t *out_handle)
{
    esp_err_t err;

    if (out_handle == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    *out_handle = NULL;
    err = validate_config(cfg);
    if (err != ESP_OK) {
        return err;
    }

    l2tap_sniffer_handle_t handle = calloc(1, sizeof(*handle));
    if (handle == NULL) {
        return ESP_ERR_NO_MEM;
    }

    normalize_config(&handle->config, cfg);
    handle->stats_lock = (portMUX_TYPE)portMUX_INITIALIZER_UNLOCKED;

    handle->sources = calloc(handle->config.filter_count, sizeof(*handle->sources));
    if (handle->sources == NULL) {
        free(handle);
        return ESP_ERR_NO_MEM;
    }

    for (size_t i = 0; i < handle->config.filter_count; ++i) {
        fill_capture_label(handle->sources[i].label, handle->config.filters[i].label);
        handle->sources[i].ethertype = handle->config.filters[i].ethertype;
        handle->sources[i].fd = L2TAP_SNIFFER_INVALID_FD;
        handle->sources[i].owner = handle;
    }

    *out_handle = handle;
    return ESP_OK;
}

esp_err_t l2tap_sniffer_start(l2tap_sniffer_handle_t handle)
{
    esp_err_t err;
    size_t started_capture_tasks = 0;

    if (handle == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (handle->started) {
        return ESP_ERR_INVALID_STATE;
    }

    memset(&handle->stats, 0, sizeof(handle->stats));

    handle->capture_ring = xRingbufferCreate(handle->config.runtime.ring_buffer_size, RINGBUF_TYPE_NOSPLIT);
    if (handle->capture_ring == NULL) {
        l2tap_sniffer_report_error(handle, ESP_ERR_NO_MEM, "Unable to allocate capture ring buffer");
        return ESP_ERR_NO_MEM;
    }

    err = l2tap_sniffer_eth_start(handle);
    if (err != ESP_OK) {
        l2tap_sniffer_report_error(handle, err, "Ethernet backend bring-up failed");
        runtime_cleanup(handle, false);
        return err;
    }

    err = l2tap_sniffer_eth_wait_ready(handle, handle->config.eth.link_timeout_ms);
    if (err != ESP_OK) {
        l2tap_sniffer_report_error(handle,
                                   err,
                                   "Ethernet did not become ready within %" PRIu32 " ms",
                                   handle->config.eth.link_timeout_ms);
        runtime_cleanup(handle, false);
        return err;
    }

    for (size_t i = 0; i < handle->config.filter_count; ++i) {
        handle->sources[i].fd = open_l2tap_fd(handle, &handle->sources[i]);
        if (handle->sources[i].fd == L2TAP_SNIFFER_INVALID_FD) {
            runtime_cleanup(handle, false);
            return ESP_FAIL;
        }
    }

    log_local_mac(handle->sources[0].fd);

    handle->running = true;

    if (xTaskCreate(analyzer_task,
                    "l2tap_analyzer",
                    L2TAP_SNIFFER_ANALYZER_TASK_STACK_SIZE,
                    handle,
                    L2TAP_SNIFFER_ANALYZER_TASK_PRIORITY,
                    &handle->analyzer_task) != pdPASS) {
        l2tap_sniffer_report_error(handle, ESP_ERR_NO_MEM, "Unable to create analyzer task");
        runtime_cleanup(handle, false);
        return ESP_ERR_NO_MEM;
    }

    if ((handle->config.runtime.stats_period_ms > 0) &&
        (xTaskCreate(stats_task,
                     "l2tap_stats",
                     L2TAP_SNIFFER_STATS_TASK_STACK_SIZE,
                     handle,
                     L2TAP_SNIFFER_STATS_TASK_PRIORITY,
                     &handle->stats_task) != pdPASS)) {
        ESP_LOGW(TAG, "Unable to create stats task, continuing without periodic counters");
        handle->stats_task = NULL;
    }

    for (size_t i = 0; i < handle->config.filter_count; ++i) {
        if (xTaskCreate(capture_task,
                        handle->sources[i].label,
                        L2TAP_SNIFFER_CAPTURE_TASK_STACK_SIZE,
                        &handle->sources[i],
                        L2TAP_SNIFFER_CAPTURE_TASK_PRIORITY,
                        &handle->sources[i].task_handle) != pdPASS) {
            l2tap_sniffer_report_error(handle,
                                       ESP_ERR_NO_MEM,
                                       "Unable to create capture task for %s",
                                       handle->sources[i].label);
            close(handle->sources[i].fd);
            handle->sources[i].fd = L2TAP_SNIFFER_INVALID_FD;
            handle->sources[i].task_handle = NULL;
            continue;
        }

        started_capture_tasks++;
    }

    if (started_capture_tasks == 0) {
        l2tap_sniffer_report_error(handle, ESP_FAIL, "No capture task could be started");
        runtime_cleanup(handle, false);
        return ESP_FAIL;
    }

    handle->started = true;
    ESP_LOGI(TAG, "Started %u capture tasks", (unsigned)started_capture_tasks);
    l2tap_sniffer_raise_event(handle, L2TAP_SNIFFER_EVENT_CAPTURE_STARTED);
    return ESP_OK;
}

esp_err_t l2tap_sniffer_stop(l2tap_sniffer_handle_t handle)
{
    if (handle == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    runtime_cleanup(handle, true);
    return ESP_OK;
}

void l2tap_sniffer_destroy(l2tap_sniffer_handle_t handle)
{
    if (handle == NULL) {
        return;
    }

    (void)l2tap_sniffer_stop(handle);
    free(handle->sources);
    free(handle);
}
