from collections import Counter

# Inventário da bancada: IP -> papel. Ajuste para o laboratório.
ATIVOS = {"192.168.0.11": "clp", "192.168.0.12": "clp",
          "192.168.0.29": "engenharia"}
PODEM_ESCREVER = {"clp", "engenharia"}


def escrita_nao_autorizada(ev):
    return (ev.direcao == "pergunta" and ev.operacao == "escrita"
            and ATIVOS.get(ev.origem) not in PODEM_ESCREVER)


def controle_do_clp(ev):
    return ev.direcao == "pergunta" and ev.operacao == "controle"


def ip_desconhecido(ev):
    return ev.origem not in ATIVOS


def resposta_de_erro(ev):
    return ev.direcao == "resposta" and ev.status != 0


REGRAS = [
    ("R01", "ALTA", "escrita de quem não pode escrever",
     escrita_nao_autorizada),
    ("R02", "CRITICA", "comando de controle no CLP", controle_do_clp),
    ("R03", "ALTA", "IP fora do inventário", ip_desconhecido),
    ("R04", "MEDIA", "resposta de erro", resposta_de_erro),
]


def avaliar(ev):
    alertas = []
    for codigo, nivel, texto, regra in REGRAS:
        if regra(ev):
            alertas.append((codigo, nivel, texto))
    return alertas


class Janela:
    """Conta eventos por (origem, destino, protocolo, operação)."""

    def __init__(self, segundos=10):
        self.segundos = segundos
        self.inicio = None
        self.contagem = Counter()

    def adicionar(self, ev):
        resumo = None
        if self.inicio is None:
            self.inicio = ev.ts
        elif ev.ts - self.inicio >= self.segundos:
            resumo = self.contagem          # a janela acabou
            self.inicio, self.contagem = ev.ts, Counter()
        chave = (ev.origem, ev.destino, ev.protocolo, ev.operacao)
        self.contagem[chave] += 1
        return resumo


if __name__ == "__main__":
    from captura import ler_arquivo
    from protocolos import decodificar
    for seg in ler_arquivo("exemplo.pcap"):
        ev = decodificar(seg)
        if ev:
            for alerta in avaliar(ev):
                print(alerta, ev)
