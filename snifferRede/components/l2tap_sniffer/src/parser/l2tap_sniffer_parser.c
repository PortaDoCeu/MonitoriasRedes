/*
 * Parser interno da biblioteca.
 * Converte quadros brutos em uma estrutura parseada estável para callbacks.
 */

#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include "arpa/inet.h"
#include "lwip/prot/ethernet.h"
#include "lwip/prot/etharp.h"
#include "lwip/prot/ip.h"
#include "lwip/prot/ip4.h"
#include "lwip/prot/tcp.h"
#include "lwip/prot/udp.h"
#include "l2tap_sniffer_internal.h"

static void format_mac(const uint8_t *mac, char out[L2TAP_SNIFFER_MAC_STR_LEN])
{
    snprintf(out, L2TAP_SNIFFER_MAC_STR_LEN, "%02x:%02x:%02x:%02x:%02x:%02x",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

static void format_ipv4_u32(uint32_t addr_net_order, char out[L2TAP_SNIFFER_IPV4_STR_LEN])
{
    uint32_t addr_host_order = ntohl(addr_net_order);

    snprintf(out, L2TAP_SNIFFER_IPV4_STR_LEN, "%" PRIu32 ".%" PRIu32 ".%" PRIu32 ".%" PRIu32,
             (addr_host_order >> 24) & 0xffU,
             (addr_host_order >> 16) & 0xffU,
             (addr_host_order >> 8) & 0xffU,
             addr_host_order & 0xffU);
}

static void format_ipv4_packed(const ip4_addr_p_t *addr, char out[L2TAP_SNIFFER_IPV4_STR_LEN])
{
    format_ipv4_u32(addr->addr, out);
}

static const char *ip_proto_name(uint8_t protocol)
{
    switch (protocol) {
    case IP_PROTO_TCP:
        return "TCP";
    case IP_PROTO_UDP:
        return "UDP";
    case IP_PROTO_ICMP:
        return "ICMP";
    case 2:
        return "IGMP";
    default:
        return "OTHER";
    }
}

static void tcp_flags_to_string(uint8_t flags, char out[L2TAP_SNIFFER_TCP_FLAG_STR_LEN])
{
    size_t offset = 0;

    out[0] = '\0';

    if (flags & TCP_FIN) {
        offset += snprintf(out + offset, L2TAP_SNIFFER_TCP_FLAG_STR_LEN - offset, "%sFIN", offset ? "|" : "");
    }
    if (flags & TCP_SYN) {
        offset += snprintf(out + offset, L2TAP_SNIFFER_TCP_FLAG_STR_LEN - offset, "%sSYN", offset ? "|" : "");
    }
    if (flags & TCP_RST) {
        offset += snprintf(out + offset, L2TAP_SNIFFER_TCP_FLAG_STR_LEN - offset, "%sRST", offset ? "|" : "");
    }
    if (flags & TCP_PSH) {
        offset += snprintf(out + offset, L2TAP_SNIFFER_TCP_FLAG_STR_LEN - offset, "%sPSH", offset ? "|" : "");
    }
    if (flags & TCP_ACK) {
        offset += snprintf(out + offset, L2TAP_SNIFFER_TCP_FLAG_STR_LEN - offset, "%sACK", offset ? "|" : "");
    }
    if (flags & TCP_URG) {
        offset += snprintf(out + offset, L2TAP_SNIFFER_TCP_FLAG_STR_LEN - offset, "%sURG", offset ? "|" : "");
    }
}

static void bytes_to_hex_preview(const l2tap_sniffer_parser_config_t *config,
                                 const uint8_t *data,
                                 size_t data_len,
                                 char *out,
                                 size_t out_len)
{
    size_t preview_len = data_len;
    size_t output_offset = 0;

    if (out_len == 0) {
        return;
    }

    out[0] = '\0';

    if (preview_len > config->payload_preview_bytes) {
        preview_len = config->payload_preview_bytes;
    }

    for (size_t i = 0; i < preview_len && (output_offset + 2) < out_len; ++i) {
        output_offset += snprintf(out + output_offset, out_len - output_offset, "%02x", data[i]);
    }
}

static void fill_payload_preview(const l2tap_sniffer_parser_config_t *config,
                                 l2tap_sniffer_parsed_frame_t *parsed,
                                 const uint8_t *payload,
                                 size_t payload_len)
{
    parsed->payload_len = payload_len;
    bytes_to_hex_preview(config, payload, payload_len, parsed->payload_preview, sizeof(parsed->payload_preview));
}

static void detect_industrial_protocol(const l2tap_sniffer_parser_config_t *config,
                                       l2tap_sniffer_parsed_frame_t *parsed)
{
    parsed->industrial[0] = '\0';

    if (!config->detect_industrial_protocols) {
        return;
    }

    if (parsed->ethertype == L2TAP_SNIFFER_ETH_TYPE_PROFINET) {
        snprintf(parsed->industrial, sizeof(parsed->industrial), "%s", "Profinet");
        return;
    }

    if (parsed->ethertype == L2TAP_SNIFFER_ETH_TYPE_ETHERCAT) {
        snprintf(parsed->industrial, sizeof(parsed->industrial), "%s", "EtherCAT");
        return;
    }

    if (!parsed->has_l4) {
        return;
    }

    if ((strcmp(parsed->transport, "TCP") == 0) &&
        ((parsed->src_port == L2TAP_SNIFFER_INDUSTRIAL_PORT_MODBUS_TCP) ||
         (parsed->dst_port == L2TAP_SNIFFER_INDUSTRIAL_PORT_MODBUS_TCP))) {
        snprintf(parsed->industrial, sizeof(parsed->industrial), "%s", "Modbus TCP");
        return;
    }

    if ((parsed->src_port == L2TAP_SNIFFER_INDUSTRIAL_PORT_ETHERNET_IP) ||
        (parsed->dst_port == L2TAP_SNIFFER_INDUSTRIAL_PORT_ETHERNET_IP)) {
        snprintf(parsed->industrial, sizeof(parsed->industrial), "%s", "EtherNet/IP");
    }
}

static bool parse_arp(const l2tap_sniffer_parser_config_t *config,
                      const uint8_t *frame,
                      size_t frame_len,
                      size_t l3_offset,
                      l2tap_sniffer_parsed_frame_t *parsed)
{
    uint32_t sender_ip = 0;
    uint32_t target_ip = 0;

    if (!config->parse_arp) {
        if (frame_len > l3_offset) {
            fill_payload_preview(config, parsed, frame + l3_offset, frame_len - l3_offset);
        }
        return true;
    }

    if (frame_len < (l3_offset + SIZEOF_ETHARP_HDR)) {
        return false;
    }

    const struct etharp_hdr *arp_hdr = (const struct etharp_hdr *)(frame + l3_offset);

    if ((arp_hdr->hwlen != ETH_HWADDR_LEN) || (arp_hdr->protolen != 4)) {
        return false;
    }

    parsed->has_arp = true;
    parsed->arp_opcode = ntohs(arp_hdr->opcode);

    memcpy(&sender_ip, &arp_hdr->sipaddr, sizeof(sender_ip));
    memcpy(&target_ip, &arp_hdr->dipaddr, sizeof(target_ip));

    format_ipv4_u32(sender_ip, parsed->arp_sender_ip);
    format_ipv4_u32(target_ip, parsed->arp_target_ip);
    return true;
}

static bool parse_ipv4_transport(const l2tap_sniffer_parser_config_t *config,
                                 const uint8_t *frame,
                                 size_t frame_len,
                                 size_t l3_offset,
                                 l2tap_sniffer_parsed_frame_t *parsed)
{
    if (!config->parse_ipv4) {
        if (frame_len > l3_offset) {
            fill_payload_preview(config, parsed, frame + l3_offset, frame_len - l3_offset);
        }
        return true;
    }

    if (frame_len < (l3_offset + IP_HLEN)) {
        return false;
    }

    const struct ip_hdr *ip_hdr = (const struct ip_hdr *)(frame + l3_offset);
    uint8_t ip_header_len = IPH_HL_BYTES(ip_hdr);
    uint16_t ip_total_len = ntohs(IPH_LEN(ip_hdr));
    size_t bytes_available = frame_len - l3_offset;
    size_t bytes_in_frame;
    uint16_t frag_field;
    uint8_t protocol;

    if ((IPH_V(ip_hdr) != 4) || (ip_header_len < IP_HLEN) ||
        (bytes_available < ip_header_len) || (ip_total_len < ip_header_len)) {
        return false;
    }

    bytes_in_frame = ip_total_len < bytes_available ? ip_total_len : bytes_available;
    frag_field = ntohs(IPH_OFFSET(ip_hdr));
    protocol = IPH_PROTO(ip_hdr);

    parsed->has_ipv4 = true;
    parsed->ip_version = IPH_V(ip_hdr);
    parsed->ip_header_len = ip_header_len;
    parsed->ip_total_len = ip_total_len;
    parsed->ip_fragment_offset = frag_field & IP_OFFMASK;
    parsed->ip_more_fragments = (frag_field & IP_MF) != 0;
    snprintf(parsed->ip_proto, sizeof(parsed->ip_proto), "%s", ip_proto_name(protocol));
    format_ipv4_packed(&ip_hdr->src, parsed->ip_src);
    format_ipv4_packed(&ip_hdr->dest, parsed->ip_dst);

    if (bytes_in_frame <= ip_header_len) {
        return true;
    }

    const uint8_t *l4_payload = frame + l3_offset + ip_header_len;
    size_t l4_available = bytes_in_frame - ip_header_len;

    if (!config->parse_transport || (parsed->ip_fragment_offset != 0)) {
        fill_payload_preview(config, parsed, l4_payload, l4_available);
        return true;
    }

    if (protocol == IP_PROTO_TCP) {
        if (l4_available < TCP_HLEN) {
            return false;
        }

        const struct tcp_hdr *tcp_hdr = (const struct tcp_hdr *)l4_payload;
        uint8_t tcp_header_len = TCPH_HDRLEN_BYTES(tcp_hdr);

        if ((tcp_header_len < TCP_HLEN) || (tcp_header_len > l4_available)) {
            return false;
        }

        parsed->has_l4 = true;
        snprintf(parsed->transport, sizeof(parsed->transport), "%s", "TCP");
        parsed->src_port = ntohs(tcp_hdr->src);
        parsed->dst_port = ntohs(tcp_hdr->dest);
        tcp_flags_to_string(TCPH_FLAGS(tcp_hdr), parsed->tcp_flags);

        fill_payload_preview(config, parsed, l4_payload + tcp_header_len, l4_available - tcp_header_len);
        return true;
    }

    if (protocol == IP_PROTO_UDP) {
        if (l4_available < UDP_HLEN) {
            return false;
        }

        const struct udp_hdr *udp_hdr = (const struct udp_hdr *)l4_payload;
        uint16_t udp_len = ntohs(udp_hdr->len);
        size_t udp_total_len = l4_available;

        if ((udp_len >= UDP_HLEN) && (udp_len < udp_total_len)) {
            udp_total_len = udp_len;
        }

        parsed->has_l4 = true;
        snprintf(parsed->transport, sizeof(parsed->transport), "%s", "UDP");
        parsed->src_port = ntohs(udp_hdr->src);
        parsed->dst_port = ntohs(udp_hdr->dest);

        fill_payload_preview(config, parsed, l4_payload + UDP_HLEN, udp_total_len - UDP_HLEN);
        return true;
    }

    fill_payload_preview(config, parsed, l4_payload, l4_available);
    return true;
}

bool l2tap_sniffer_parse_frame_internal(const l2tap_sniffer_parser_config_t *config,
                                        const l2tap_sniffer_raw_frame_t *raw_frame,
                                        l2tap_sniffer_parsed_frame_t *parsed_frame)
{
    const uint8_t *frame = raw_frame->frame;
    size_t frame_len = raw_frame->frame_len;
    uint16_t current_ethertype;
    size_t l3_offset = SIZEOF_ETH_HDR;
    int vlan_id = -1;

    memset(parsed_frame, 0, sizeof(*parsed_frame));
    parsed_frame->vlan_id = -1;

    if (frame_len < SIZEOF_ETH_HDR) {
        return false;
    }

    const struct eth_hdr *eth_hdr = (const struct eth_hdr *)frame;
    format_mac(eth_hdr->src.addr, parsed_frame->src_mac);
    format_mac(eth_hdr->dest.addr, parsed_frame->dst_mac);

    parsed_frame->outer_ethertype = ntohs(eth_hdr->type);
    current_ethertype = parsed_frame->outer_ethertype;

    for (int depth = 0; depth < 2; ++depth) {
        if ((current_ethertype != L2TAP_SNIFFER_ETH_TYPE_VLAN) &&
            (current_ethertype != L2TAP_SNIFFER_ETH_TYPE_QINQ)) {
            break;
        }

        if (frame_len < (l3_offset + SIZEOF_VLAN_HDR)) {
            return false;
        }

        const struct eth_vlan_hdr *vlan_hdr = (const struct eth_vlan_hdr *)(frame + l3_offset);
        vlan_id = ntohs(vlan_hdr->prio_vid) & 0x0fff;
        current_ethertype = ntohs(vlan_hdr->tpid);
        l3_offset += SIZEOF_VLAN_HDR;
    }

    parsed_frame->ethertype = current_ethertype;
    parsed_frame->vlan_id = vlan_id;

    switch (parsed_frame->ethertype) {
    case L2TAP_SNIFFER_ETH_TYPE_ARP:
        if (!parse_arp(config, frame, frame_len, l3_offset, parsed_frame)) {
            return false;
        }
        break;
    case L2TAP_SNIFFER_ETH_TYPE_IPV4:
        if (!parse_ipv4_transport(config, frame, frame_len, l3_offset, parsed_frame)) {
            return false;
        }
        break;
    default:
        if (frame_len > l3_offset) {
            fill_payload_preview(config, parsed_frame, frame + l3_offset, frame_len - l3_offset);
        }
        break;
    }

    detect_industrial_protocol(config, parsed_frame);
    return true;
}
