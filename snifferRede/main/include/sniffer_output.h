/*
 * Helpers do exemplo para serializar os frames parseados em JSON na UART.
 */

#ifndef SNIFFER_OUTPUT_H
#define SNIFFER_OUTPUT_H

#include "l2tap_sniffer_types.h"

void sniffer_output_emit_json(const l2tap_sniffer_raw_frame_t *raw_frame,
                              const l2tap_sniffer_parsed_frame_t *parsed_frame);

#endif
