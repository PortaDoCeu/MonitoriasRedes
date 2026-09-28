"""Contrato de dados do projeto (Arquitetura.md, seção 5; ADR-006).

Fonte única de endereços, escalas, bits e tópicos. O gateway e o CLP simulado
importam daqui; nenhum outro arquivo deve ter endereço Modbus escrito à mão.
"""

# ---------------------------------------------------------------- registradores (base 0)

TOTAL_REGISTRADORES = 100      # DB do MB_SERVER: Array[0..99] of Word (ADR-004)

# Área de leitura (o CLP escreve, o gateway lê)
HR_TEMPERATURA = 0             # Int com sinal, °C x 10
HR_VELOCIDADE = 1              # rpm
HR_STATUS = 2                  # palavra de bits
HR_REFERENCIA = 3              # rpm aplicados pelo CLP
HR_FALHA = 4                   # código de falha
LEITURA_INICIO = 0
LEITURA_QUANTIDADE = 10        # HR0 a HR9 numa única FC 3

# Área de escrita (o gateway escreve, o CLP lê)
HR_CMD_VELOCIDADE = 10         # referência pedida, rpm
HR_CMD_MOTOR = 11              # 0 parar, 1 ligar, 2 reconhecer falha
HR_HEARTBEAT = 12              # contador, +1 por ciclo

ESCALA_TEMPERATURA = 10

CMD_PARAR = 0
CMD_LIGAR = 1
CMD_RECONHECER = 2
COMANDOS_MOTOR = (CMD_PARAR, CMD_LIGAR, CMD_RECONHECER)

# Bits da palavra de status (HR2), na ordem do bit 0 em diante
BITS_STATUS = [
    "motor_ligado",
    "modo_remoto",
    "falha_inversor",
    "heartbeat_perdido",
    "referencia_limitada",
    "emergencia",
]

FALHAS = {
    0: "sem falha",
    1: "falha no inversor",
    2: "heartbeat perdido",
    3: "emergencia acionada",
    4: "temperatura acima do limite",
    5: "leitura do termopar invalida",
}


# ---------------------------------------------------------------- tópicos MQTT

def topicos(bancada):
    """Tópicos de uma bancada. Ex.: topicos("bancada3")["temperatura"]."""
    return {
        "temperatura": f"{bancada}/telemetria/temperatura",
        "velocidade": f"{bancada}/telemetria/velocidade",
        "referencia": f"{bancada}/telemetria/referencia",
        "status": f"{bancada}/telemetria/status",
        "cmd_velocidade": f"{bancada}/comando/velocidade",
        "cmd_motor": f"{bancada}/comando/motor",
        "resposta": f"{bancada}/comando/resposta",
        "estado": f"{bancada}/gateway/estado",
    }


# ---------------------------------------------------------------- conversões

def para_int16(valor):
    """Registrador Modbus (0 a 65535) para inteiro com sinal (-32768 a 32767)."""
    return valor - 65536 if valor >= 32768 else valor


def para_word(valor):
    """Inteiro com sinal para registrador Modbus (0 a 65535)."""
    return valor & 0xFFFF


def decodificar_status(palavra, codigo_falha):
    """Palavra de bits (HR2) e código de falha (HR4) para o dicionário do JSON de status."""
    status = {nome: bool(palavra >> bit & 1) for bit, nome in enumerate(BITS_STATUS)}
    status["codigo_falha"] = codigo_falha
    return status


def codificar_status(status):
    """Operação inversa de decodificar_status (usada pelo CLP simulado)."""
    palavra = 0
    for bit, nome in enumerate(BITS_STATUS):
        if status.get(nome):
            palavra |= 1 << bit
    return palavra


def decodificar_leitura(registradores):
    """Os 10 registradores de HR0 a HR9 para valores em unidade de engenharia."""
    return {
        "temperatura": para_int16(registradores[HR_TEMPERATURA]) / ESCALA_TEMPERATURA,
        "velocidade": registradores[HR_VELOCIDADE],
        "referencia": registradores[HR_REFERENCIA],
        "status": decodificar_status(registradores[HR_STATUS], registradores[HR_FALHA]),
    }
