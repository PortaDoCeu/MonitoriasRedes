/*
 * API pública da biblioteca l2tap_sniffer.
 */

#ifndef L2TAP_SNIFFER_H
#define L2TAP_SNIFFER_H

#include "l2tap_sniffer_types.h"

#ifdef __cplusplus
extern "C" {
#endif

l2tap_sniffer_runtime_config_t l2tap_sniffer_runtime_config_default(void);
l2tap_sniffer_parser_config_t l2tap_sniffer_parser_config_default(void);
l2tap_sniffer_esp32_eth_config_t l2tap_sniffer_esp32_eth_config_default(void);
l2tap_sniffer_config_t l2tap_sniffer_config_default(void);

esp_err_t l2tap_sniffer_create(const l2tap_sniffer_config_t *cfg, l2tap_sniffer_handle_t *out_handle);
esp_err_t l2tap_sniffer_start(l2tap_sniffer_handle_t handle);
esp_err_t l2tap_sniffer_stop(l2tap_sniffer_handle_t handle);
void l2tap_sniffer_destroy(l2tap_sniffer_handle_t handle);

#ifdef __cplusplus
}
#endif

#endif
