/*
 * Estruturas e helpers internos compartilhados pelos módulos da biblioteca.
 */

#ifndef L2TAP_SNIFFER_INTERNAL_H
#define L2TAP_SNIFFER_INTERNAL_H

#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/ringbuf.h"
#include "freertos/task.h"
#include "esp_eth.h"
#include "esp_netif.h"
#include "l2tap_sniffer.h"
#include "l2tap_sniffer_defaults.h"

typedef struct l2tap_sniffer_capture_source {
    char label[L2TAP_SNIFFER_CAPTURE_LABEL_LEN];
    uint16_t ethertype;
    int fd;
    TaskHandle_t task_handle;
    l2tap_sniffer_handle_t owner;
} l2tap_sniffer_capture_source_t;

typedef struct {
    EventGroupHandle_t event_group;
    esp_eth_handle_t handle;
    esp_netif_t *netif;
    esp_eth_netif_glue_handle_t glue;
} l2tap_sniffer_eth_state_t;

struct l2tap_sniffer {
    l2tap_sniffer_config_t config;
    l2tap_sniffer_capture_source_t *sources;
    RingbufHandle_t capture_ring;
    TaskHandle_t analyzer_task;
    TaskHandle_t stats_task;
    portMUX_TYPE stats_lock;
    l2tap_sniffer_stats_t stats;
    l2tap_sniffer_eth_state_t eth;
    bool started;
    bool running;
};

void l2tap_sniffer_raise_event(l2tap_sniffer_handle_t handle, l2tap_sniffer_event_t event);
void l2tap_sniffer_report_error(l2tap_sniffer_handle_t handle, esp_err_t err, const char *fmt, ...);

esp_err_t l2tap_sniffer_eth_start(l2tap_sniffer_handle_t handle);
esp_err_t l2tap_sniffer_eth_wait_ready(l2tap_sniffer_handle_t handle, uint32_t timeout_ms);
void l2tap_sniffer_eth_stop(l2tap_sniffer_handle_t handle);

bool l2tap_sniffer_parse_frame_internal(const l2tap_sniffer_parser_config_t *config,
                                        const l2tap_sniffer_raw_frame_t *raw_frame,
                                        l2tap_sniffer_parsed_frame_t *parsed_frame);

#endif
