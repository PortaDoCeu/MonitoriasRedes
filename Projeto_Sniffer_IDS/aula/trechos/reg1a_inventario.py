from collections import Counter

# Inventário da bancada: IP -> papel. Ajuste para o laboratório.
ATIVOS = {"192.168.0.11": "clp", "192.168.0.12": "clp",
          "192.168.0.29": "engenharia"}
PODEM_ESCREVER = {"clp", "engenharia"}


def escrita_nao_autorizada(ev):
    return (ev.direcao == "pergunta" and ev.operacao == "escrita"
            and ATIVOS.get(ev.origem) not in PODEM_ESCREVER)
