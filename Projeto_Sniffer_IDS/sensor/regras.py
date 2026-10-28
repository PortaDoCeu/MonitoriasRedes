"""Etapa 4: detectar.

Cada regra é uma função pequena que recebe um Evento e responde True (suspeito) ou False.
A Janela conta o que aconteceu a cada N segundos: é o resumo que o modelo de IA do TCC usa.

Em C (ESP32): módulos assets, rules e stats. Lá cada regra é uma linha de dados numa
tabela const (protocolo, operação, papel proibido, faixa de endereços), não uma função,
e a janela é uma tabela de tamanho fixo.
"""

from collections import Counter
from dataclasses import dataclass

# Inventário da bancada: IP -> papel. Ajuste para os IPs do laboratório.
ATIVOS = {
    "192.168.0.11": "clp",
    "192.168.0.12": "clp",
    "192.168.0.29": "engenharia",
}
PODEM_ESCREVER = {"engenharia", "clp"}      # CLPs escrevem uns nos outros (PUT/GET)

SILENCIO = 10.0                             # segundos sem repetir o mesmo alerta


@dataclass
class Alerta:
    regra: str
    severidade: str
    descricao: str
    evento: object

    def __str__(self):
        return f"!!! [{self.regra}] {self.severidade.upper():7} {self.descricao}\n    {self.evento}"


# ---------------------------------------------------------------- as regras

def escrita_nao_autorizada(ev):
    return (ev.direcao == "pergunta" and ev.operacao == "escrita"
            and ATIVOS.get(ev.origem) not in PODEM_ESCREVER)


def controle_do_clp(ev):
    return ev.direcao == "pergunta" and ev.operacao == "controle"


def ip_desconhecido(ev):
    return ev.origem not in ATIVOS or ev.destino not in ATIVOS


def resposta_de_erro(ev):
    return ev.direcao == "resposta" and ev.status != 0


REGRAS = [
    ("R01", "alta", "escrita vinda de quem não pode escrever", escrita_nao_autorizada),
    ("R02", "critica", "comando de controle no CLP (stop, start, programa)", controle_do_clp),
    ("R03", "alta", "IP fora do inventário", ip_desconhecido),
    ("R05", "media", "resposta de erro (acesso negado, endereço inválido)", resposta_de_erro),
]

ultimo_aviso = {}                           # (regra, origem, destino) -> hora do último alerta


def avaliar(ev):
    """Devolve a lista de alertas para este evento, sem repetir o mesmo alerta seguido."""
    alertas = []
    for codigo, severidade, descricao, regra in REGRAS:
        if not regra(ev):
            continue
        chave = (codigo, ev.origem, ev.destino)
        if ev.ts - ultimo_aviso.get(chave, -SILENCIO) < SILENCIO:
            continue                        # já avisou há pouco
        ultimo_aviso[chave] = ev.ts
        alertas.append(Alerta(codigo, severidade, descricao, ev))
    return alertas


# ---------------------------------------------------------------- estatísticas por janela

class Janela:
    """Conta eventos por (origem, destino, protocolo, operação) a cada `segundos`."""

    def __init__(self, segundos=10):
        self.segundos = segundos
        self.inicio = None
        self.contagem = Counter()
        self.valores = {}                   # (servidor, área, endereço) -> últimos valores

    def adicionar(self, ev):
        """Soma o evento. Se a janela acabou, devolve o resumo dela e começa outra."""
        resumo = None
        if self.inicio is None:
            self.inicio = ev.ts
        elif ev.ts - self.inicio >= self.segundos:
            resumo = {"inicio": self.inicio, "contagem": self.contagem, "valores": self.valores}
            self.inicio, self.contagem, self.valores = ev.ts, Counter(), {}

        self.contagem[(ev.origem, ev.destino, ev.protocolo, ev.operacao)] += 1
        if ev.valores:
            servidor = ev.destino if ev.direcao == "pergunta" else ev.origem
            self.valores[(servidor, ev.area, ev.endereco)] = ev.valores
        return resumo
