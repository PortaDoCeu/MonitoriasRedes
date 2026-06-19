/*
 * Saída JSON do exemplo.
 * A biblioteca é agnóstica ao formato de saída; a serialização fica na aplicação.
 */

#include <inttypes.h>
#include <stdio.h>
#include "sniffer_output.h"

int sniffer_output_format_json(char *out,
                               size_t out_len,
                               const l2tap_sniffer_raw_frame_t *raw_frame,
                               const l2tap_sniffer_parsed_frame_t *parsed_frame)
{
    (void)raw_frame;

    return snprintf(
        out,
        out_len,
        "{\"ip_src\":\"%s\",\"ip_dst\":\"%s\"}",

        parsed_frame->ip_src,
        parsed_frame->ip_dst);
}

void sniffer_output_emit_json(const l2tap_sniffer_raw_frame_t *raw_frame,
                              const l2tap_sniffer_parsed_frame_t *parsed_frame)
{
    char json[1024];

    if (sniffer_output_format_json(json, sizeof(json), raw_frame, parsed_frame) < 0) {
        return;
    }

    printf("%s\n", json);
}
