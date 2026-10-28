/* parse_l2l4: o driver entrega o quadro cru; cada cabeçalho é conferido à mão */
int parse_l2l4(const uint8_t *q, size_t len, frame_info_t *fi) {
    if (len < 14 + 20 + 20) return -1;            /* pequeno demais        */
    if (rd16(q + 12) != 0x0800) return -1;        /* não é IPv4            */
    const uint8_t *ip = q + 14;
    size_t ihl = (ip[0] & 0x0F) * 4;              /* o mesmo "* 4"         */
    if (ip[9] != 6) return -1;                    /* protocolo 6 = TCP     */
    const uint8_t *tcp = ip + ihl;
    size_t doff = (tcp[12] >> 4) * 4;
    size_t total = rd16(ip + 2);                  /* ip.len                */
    if (total > len - 14 || ihl + doff > total) return -1;
    fi->src_ip = rd32(ip + 12);  fi->dst_ip = rd32(ip + 16);
    fi->src_port = rd16(tcp);    fi->dst_port = rd16(tcp + 2);
    fi->payload = tcp + doff;                     /* aponta, não copia     */
    fi->payload_len = total - ihl - doff;
    return 0;
}
