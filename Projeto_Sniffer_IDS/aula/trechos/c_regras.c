typedef struct {
    const char *id;     uint8_t severity;
    uint8_t  proto_id;  uint8_t op;        /* ANY = qualquer          */
    uint8_t  src_role_not;                 /* dispara se a origem NÃO */
    uint16_t rate_max_per_s;               /* 0 = sem limite de taxa  */
} rule_t;

static const rule_t RULES[] = {            /* gravado no firmware     */
    { "R01", SEV_HIGH, ANY, OP_WRITE,   ROLE_ENG | ROLE_PLC, 0 },
    { "R02", SEV_CRIT, ANY, OP_CONTROL, ROLE_NONE,           0 },
    { "R04", SEV_MED,  ANY, OP_ANY,     ROLE_NONE,          50 },
};
