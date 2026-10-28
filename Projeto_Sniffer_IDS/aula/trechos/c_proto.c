typedef struct proto {
    const char *name;
    uint16_t    tcp_port;                     /* 502, 102                   */
    /* tamanho da próxima mensagem: >0 bytes, 0 falta chegar, <0 lixo     */
    int  (*frame_len)(const uint8_t *buf, size_t len);
    /* decodifica UMA mensagem inteira e preenche o evento                */
    int  (*decode)(const uint8_t *msg, size_t len, msg_dir_t dir,
                   proto_state_t *st, event_t *out);
} proto_t;

static const proto_t *const PROTOS[] = { &PROTO_MODBUS, &PROTO_S7 };

static int modbus_frame_len(const uint8_t *b, size_t n) {
    if (n < 6) return 0;                          /* falta o MBAP          */
    if (rd16(b + 2) != 0) return -1;              /* Protocol ID != 0      */
    return 6 + rd16(b + 4);                       /* o mesmo 6 + tamanho   */
}
