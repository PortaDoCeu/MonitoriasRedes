/*
 * Saída JSON do exemplo.
 * A biblioteca é agnóstica ao formato de saída; a serialização fica na aplicação.
 */

#include <inttypes.h>
#include <stdio.h>
#include "sniffer_output.h"

void sniffer_output_emit_json(const l2tap_sniffer_raw_frame_t *raw_frame,
                              const l2tap_sniffer_parsed_frame_t *parsed_frame)
{
    printf(
        "{\"ts_us\":%" PRId64 ",\"capture\":\"%s\",\"frame_len\":%u,"
        "\"src_mac\":\"%s\",\"dst_mac\":\"%s\","
        "\"outer_ethertype\":\"0x%04x\",\"ethertype\":\"0x%04x\",\"vlan_id\":%d,"
        "\"has_arp\":%s,\"arp_opcode\":%u,\"arp_sender_ip\":\"%s\",\"arp_target_ip\":\"%s\","
        "\"has_ipv4\":%s,\"ip_version\":%u,\"ip_header_len\":%u,\"ip_total_len\":%u,"
        "\"ip_fragment_offset\":%u,\"ip_more_fragments\":%s,"
        "\"ip_proto\":\"%s\",\"ip_src\":\"%s\",\"ip_dst\":\"%s\","
        "\"has_l4\":%s,\"transport\":\"%s\",\"src_port\":%u,\"dst_port\":%u,\"tcp_flags\":\"%s\","
        "\"payload_len\":%u,\"payload_preview\":\"%s\",\"industrial\":\"%s\"}\n",
        raw_frame->ts_us,
        raw_frame->capture_label,
        raw_frame->frame_len,
        parsed_frame->src_mac,
        parsed_frame->dst_mac,
        parsed_frame->outer_ethertype,
        parsed_frame->ethertype,
        parsed_frame->vlan_id,
        parsed_frame->has_arp ? "true" : "false",
        parsed_frame->arp_opcode,
        parsed_frame->arp_sender_ip,
        parsed_frame->arp_target_ip,
        parsed_frame->has_ipv4 ? "true" : "false",
        parsed_frame->ip_version,
        parsed_frame->ip_header_len,
        parsed_frame->ip_total_len,
        parsed_frame->ip_fragment_offset,
        parsed_frame->ip_more_fragments ? "true" : "false",
        parsed_frame->ip_proto,
        parsed_frame->ip_src,
        parsed_frame->ip_dst,
        parsed_frame->has_l4 ? "true" : "false",
        parsed_frame->transport,
        parsed_frame->src_port,
        parsed_frame->dst_port,
        parsed_frame->tcp_flags,
        (unsigned)parsed_frame->payload_len,
        parsed_frame->payload_preview,
        parsed_frame->industrial);
}
