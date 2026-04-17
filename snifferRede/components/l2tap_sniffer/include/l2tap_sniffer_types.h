/*
 * Tipos públicos da biblioteca l2tap_sniffer.
 */

#ifndef L2TAP_SNIFFER_TYPES_H
#define L2TAP_SNIFFER_TYPES_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"

#define L2TAP_SNIFFER_CAPTURE_LABEL_LEN         24
#define L2TAP_SNIFFER_MAC_STR_LEN               18
#define L2TAP_SNIFFER_IPV4_STR_LEN              16
#define L2TAP_SNIFFER_IP_PROTO_STR_LEN          12
#define L2TAP_SNIFFER_TCP_FLAG_STR_LEN          32
#define L2TAP_SNIFFER_INDUSTRIAL_STR_LEN        24
#define L2TAP_SNIFFER_MAX_PAYLOAD_PREVIEW_BYTES 256
#define L2TAP_SNIFFER_PREVIEW_STR_LEN           ((L2TAP_SNIFFER_MAX_PAYLOAD_PREVIEW_BYTES * 2) + 1)

#define L2TAP_SNIFFER_ETH_TYPE_IPV4             0x0800
#define L2TAP_SNIFFER_ETH_TYPE_ARP              0x0806
#define L2TAP_SNIFFER_ETH_TYPE_VLAN             0x8100
#define L2TAP_SNIFFER_ETH_TYPE_QINQ             0x88A8
#define L2TAP_SNIFFER_ETH_TYPE_PROFINET         0x8892
#define L2TAP_SNIFFER_ETH_TYPE_ETHERCAT         0x88A4

typedef struct l2tap_sniffer *l2tap_sniffer_handle_t;

typedef enum {
    L2TAP_SNIFFER_PHY_RTL8201 = 0,
} l2tap_sniffer_phy_t;

typedef enum {
    L2TAP_SNIFFER_EVENT_ETH_STARTED = 0,
    L2TAP_SNIFFER_EVENT_LINK_UP,
    L2TAP_SNIFFER_EVENT_IP_ACQUIRED,
    L2TAP_SNIFFER_EVENT_CAPTURE_STARTED,
    L2TAP_SNIFFER_EVENT_STOPPED,
    L2TAP_SNIFFER_EVENT_ERROR,
} l2tap_sniffer_event_t;

typedef struct {
    const char *label;
    uint16_t ethertype;
} l2tap_sniffer_filter_t;

typedef struct {
    bool parse_arp;
    bool parse_ipv4;
    bool parse_transport;
    bool detect_industrial_protocols;
    size_t payload_preview_bytes;
} l2tap_sniffer_parser_config_t;

typedef struct {
    size_t max_frame_len;
    size_t ring_buffer_size;
    uint32_t stats_period_ms;
} l2tap_sniffer_runtime_config_t;

typedef struct {
    int power_gpio;
    int mdc_gpio;
    int mdio_gpio;
    int phy_addr;
    int rmii_clk_gpio;
    int phy_reset_gpio;
    uint32_t power_up_delay_ms;
    uint32_t link_timeout_ms;
    l2tap_sniffer_phy_t phy;
} l2tap_sniffer_esp32_eth_config_t;

typedef struct {
    char capture_label[L2TAP_SNIFFER_CAPTURE_LABEL_LEN];
    int64_t ts_us;
    uint16_t source_filter;
    uint16_t frame_len;
    uint8_t frame[];
} l2tap_sniffer_raw_frame_t;

typedef struct {
    char src_mac[L2TAP_SNIFFER_MAC_STR_LEN];
    char dst_mac[L2TAP_SNIFFER_MAC_STR_LEN];
    uint16_t outer_ethertype;
    uint16_t ethertype;
    int vlan_id;

    bool has_arp;
    uint16_t arp_opcode;
    char arp_sender_ip[L2TAP_SNIFFER_IPV4_STR_LEN];
    char arp_target_ip[L2TAP_SNIFFER_IPV4_STR_LEN];

    bool has_ipv4;
    uint8_t ip_version;
    uint8_t ip_header_len;
    uint16_t ip_total_len;
    uint16_t ip_fragment_offset;
    bool ip_more_fragments;
    char ip_proto[L2TAP_SNIFFER_IP_PROTO_STR_LEN];
    char ip_src[L2TAP_SNIFFER_IPV4_STR_LEN];
    char ip_dst[L2TAP_SNIFFER_IPV4_STR_LEN];

    bool has_l4;
    char transport[4];
    uint16_t src_port;
    uint16_t dst_port;
    char tcp_flags[L2TAP_SNIFFER_TCP_FLAG_STR_LEN];

    size_t payload_len;
    char payload_preview[L2TAP_SNIFFER_PREVIEW_STR_LEN];
    char industrial[L2TAP_SNIFFER_INDUSTRIAL_STR_LEN];
} l2tap_sniffer_parsed_frame_t;

typedef struct {
    uint32_t captured;
    uint32_t enqueued;
    uint32_t emitted;
    uint32_t ring_drops;
    uint32_t read_errors;
    uint32_t parse_errors;
} l2tap_sniffer_stats_t;

typedef void (*l2tap_sniffer_on_raw_frame_cb)(l2tap_sniffer_handle_t handle,
                                              const l2tap_sniffer_raw_frame_t *raw_frame,
                                              void *user_ctx);

typedef void (*l2tap_sniffer_on_parsed_frame_cb)(l2tap_sniffer_handle_t handle,
                                                 const l2tap_sniffer_raw_frame_t *raw_frame,
                                                 const l2tap_sniffer_parsed_frame_t *parsed_frame,
                                                 void *user_ctx);

typedef void (*l2tap_sniffer_on_event_cb)(l2tap_sniffer_handle_t handle,
                                          l2tap_sniffer_event_t event,
                                          void *user_ctx);

typedef void (*l2tap_sniffer_on_error_cb)(l2tap_sniffer_handle_t handle,
                                          esp_err_t err,
                                          const char *message,
                                          void *user_ctx);

typedef struct {
    l2tap_sniffer_on_raw_frame_cb on_raw_frame;
    l2tap_sniffer_on_parsed_frame_cb on_parsed_frame;
    l2tap_sniffer_on_event_cb on_event;
    l2tap_sniffer_on_error_cb on_error;
    void *user_ctx;
} l2tap_sniffer_callbacks_t;

typedef struct {
    const char *interface_name;
    const l2tap_sniffer_filter_t *filters;
    size_t filter_count;
    l2tap_sniffer_runtime_config_t runtime;
    l2tap_sniffer_parser_config_t parser;
    l2tap_sniffer_esp32_eth_config_t eth;
    l2tap_sniffer_callbacks_t callbacks;
} l2tap_sniffer_config_t;

#endif
