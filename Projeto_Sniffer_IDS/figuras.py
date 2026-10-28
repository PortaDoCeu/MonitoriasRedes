"""Figuras do documento de arquitetura (Projeto_Sniffer_IDS).

Gera os PNGs em img/. Para mudar uma figura, edite a função e rode de novo:

    python figuras.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

PASTA = Path(__file__).parent / "img"
PASTA.mkdir(exist_ok=True)

# Paleta (mesma família de cores do tema dos slides)
NAVY = "#111827"
INK = "#1F2937"
MUTED = "#5B6677"
CIANO = "#0B7F7D"
CIANO_BG = "#EAF6F6"
AMBAR = "#B7791F"
AMBAR_BG = "#FDF3E1"
CINZA = "#5B6677"
CINZA_BG = "#EEF0F4"
VERMELHO = "#C53030"

plt.rcParams["font.family"] = "DejaVu Sans"


# ---------------------------------------------------------------- peças

def nova_figura(largura, altura, escala=0.75):
    fig, ax = plt.subplots(figsize=(largura * escala, altura * escala))
    ax.set_xlim(0, largura)
    ax.set_ylim(0, altura)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def zona(ax, x, y, w, h, titulo, cor, fundo):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.25",
                                facecolor=fundo, edgecolor=cor, linewidth=1.6,
                                linestyle=(0, (5, 3)), zorder=0))
    ax.text(x + 0.25, y + h - 0.3, titulo, color=cor, fontsize=11,
            fontweight="bold", va="top", ha="left")


def bloco(ax, x, y, w, h, titulo, sub="", cor=NAVY):
    """Caixa branca com título em negrito e subtítulo."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor="white", edgecolor=cor, linewidth=2, zorder=2))
    cx = x + w / 2
    if sub:
        ax.text(cx, y + h * 0.68, titulo, ha="center", va="center", fontsize=11,
                fontweight="bold", color=NAVY, zorder=3)
        ax.text(cx, y + h * 0.32, sub, ha="center", va="center", fontsize=8.5,
                color=MUTED, zorder=3, linespacing=1.3)
    else:
        ax.text(cx, y + h / 2, titulo, ha="center", va="center", fontsize=11,
                fontweight="bold", color=NAVY, zorder=3)


def seta(ax, p1, p2, dupla=False, cor=INK, tracejada=False, lw=1.8):
    estilo = "<|-|>" if dupla else "-|>"
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=estilo, mutation_scale=14,
                                 color=cor, lw=lw, zorder=1,
                                 linestyle="--" if tracejada else "-"))


def linha(ax, pontos, cor=INK, lw=1.8, tracejada=False):
    xs, ys = zip(*pontos)
    ax.plot(xs, ys, color=cor, lw=lw, zorder=1, solid_capstyle="round",
            linestyle="--" if tracejada else "-")


def caminho(ax, pontos, cor=INK, tracejada=False):
    """Linha com cotovelos e seta só no último segmento."""
    if len(pontos) > 2:
        linha(ax, pontos[:-1], cor=cor, tracejada=tracejada)
    seta(ax, pontos[-2], pontos[-1], cor=cor, tracejada=tracejada)


def rotulo(ax, x, y, texto, cor=INK, tam=9, **kw):
    ax.text(x, y, texto, ha="center", va="center", fontsize=tam, color=cor,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor="none", alpha=0.95), zorder=5, **kw)


def salvar(fig, nome):
    fig.savefig(PASTA / nome, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("gerado:", PASTA / nome)


# ---------------------------------------------------------------- implantação

def fig_implantacao():
    """Onde o sensor fica: escuta a planta pelo espelho e publica por Wi-Fi."""
    fig, ax = nova_figura(23.0, 8.0)

    zona(ax, 0.2, 0.3, 8.8, 7.4, "Rede da planta (OT)", AMBAR, AMBAR_BG)
    zona(ax, 11.5, 0.3, 3.2, 7.4, "Sensor", CINZA, CINZA_BG)
    zona(ax, 15.6, 0.3, 7.2, 7.4, "Rede de gestão (TI)", CIANO, CIANO_BG)

    bloco(ax, 0.6, 5.0, 2.4, 1.4, "CLP A", "S7-1200", AMBAR)
    bloco(ax, 0.6, 2.9, 2.4, 1.4, "CLP B", "S7-1200", AMBAR)
    bloco(ax, 0.6, 0.8, 2.4, 1.4, "IHM / estação", "engenharia", AMBAR)
    bloco(ax, 5.2, 2.6, 2.6, 2.0, "Switch", "gerenciado\nporta espelho", AMBAR)

    linha(ax, [(4.0, 5.7), (4.0, 1.5)])
    for y in (5.7, 3.6, 1.5):
        linha(ax, [(3.0, y), (4.0, y)])
    seta(ax, (4.0, 3.6), (5.2, 3.6), dupla=True)

    bloco(ax, 11.8, 2.6, 2.6, 2.0, "Sensor", "ESP32\nLILYGO T-ETH-Lite", NAVY)
    seta(ax, (7.8, 3.6), (11.8, 3.6), cor=VERMELHO, lw=2.2)
    rotulo(ax, 10.25, 4.15, "SPAN: só recebe", cor=VERMELHO, tam=9)
    rotulo(ax, 10.25, 3.05, "Ethernet sem IP", cor=VERMELHO, tam=8.5)

    bloco(ax, 16.6, 2.6, 2.4, 2.0, "Broker", "MQTT", CIANO)
    seta(ax, (14.4, 3.6), (16.6, 3.6), cor=CIANO, lw=2.2)
    rotulo(ax, 15.15, 4.15, "Wi-Fi", cor=CIANO, tam=9)

    bloco(ax, 20.3, 4.9, 2.2, 1.6, "Painel", "alertas", CIANO)
    bloco(ax, 20.3, 0.8, 2.2, 1.6, "Modelo de IA", "TCC (séries\ntemporais)", CIANO)
    caminho(ax, [(19.0, 3.9), (19.65, 3.9), (19.65, 5.7), (20.3, 5.7)], cor=CIANO)
    caminho(ax, [(19.0, 3.3), (19.65, 3.3), (19.65, 1.6), (20.3, 1.6)], cor=CIANO)

    salvar(fig, "implantacao.png")


# ---------------------------------------------------------------- sensor em C

def fig_arquitetura_c():
    """Módulos do firmware no ESP32: núcleo 1 analisa, núcleo 0 comunica."""
    fig, ax = nova_figura(22.0, 11.0)

    zona(ax, 0.2, 4.6, 21.6, 6.1, "Núcleo 1: captura e análise (uma tarefa, sem travas)", AMBAR, AMBAR_BG)
    zona(ax, 0.2, 0.3, 21.6, 3.9, "Núcleo 0: comunicação", CIANO, CIANO_BG)

    plat, port = NAVY, CIANO  # borda escura = plataforma (ESP-IDF); ciano = núcleo portável (C99)
    y, h, w = 7.0, 1.7, 2.6
    bloco(ax, 0.6, y, w, h, "eth_cap", "driver promíscuo\nsem pilha IP", plat)
    bloco(ax, 3.9, y, w, h, "pool", "32 buffers fixos\nde 1536 B", port)
    bloco(ax, 7.2, y, w, h, "parse_l2l4", "Ethernet, VLAN\nIPv4, TCP", port)
    bloco(ax, 10.5, y, w, h, "flow", "32 fluxos\nremontagem limitada", port)
    bloco(ax, 13.8, y, w, h, "proto", "plugins:\nModbus, S7comm…", port)

    for x1, x2, txt in ((3.2, 3.9, ""), (6.5, 7.2, "fila"), (9.8, 10.5, ""), (13.1, 13.8, "")):
        seta(ax, (x1, y + h / 2), (x2, y + h / 2))
        if txt:
            rotulo(ax, (x1 + x2) / 2, y + h + 0.3, txt, tam=8.5)

    bloco(ax, 17.4, y, 2.6, h, "rules", "regras compiladas", port)
    bloco(ax, 20.3, y + 0.2, 1.3, 1.3, "assets", "", port)
    seta(ax, (20.3, y + h / 2), (20.0, y + h / 2), tracejada=True)
    bloco(ax, 13.8, 4.9, w, 1.5, "stats", "janela de 10 s", port)

    seta(ax, (16.4, y + h / 2), (17.4, y + h / 2))
    rotulo(ax, 16.9, y + h + 0.3, "event_t", tam=8.5)
    seta(ax, (15.1, y), (15.1, 6.4))

    bloco(ax, 14.0, 1.3, 2.8, 1.7, "fila de saída", "alertas têm\nprioridade", port)
    bloco(ax, 17.9, 1.3, 2.8, 1.7, "uplink_mqtt", "Wi-Fi + TLS", plat)
    bloco(ax, 9.6, 1.3, 2.6, 1.7, "health", "contadores\nwatchdog", plat)
    bloco(ax, 0.6, 1.3, 2.6, 1.7, "clock", "esp_timer\nSNTP", plat)
    bloco(ax, 3.9, 1.3, 2.6, 1.7, "cfg", "tamanhos, portas\nID do sensor", plat)

    caminho(ax, [(18.7, y), (18.7, 3.7), (16.2, 3.7), (16.2, 3.0)])
    seta(ax, (15.1, 4.9), (15.1, 3.0))
    rotulo(ax, 18.7, 5.6, "alert_t", tam=8.5)
    rotulo(ax, 15.1, 4.45, "stats_window_t", tam=8.5)
    seta(ax, (12.2, 2.15), (14.0, 2.15))
    seta(ax, (16.8, 2.15), (17.9, 2.15))
    seta(ax, (20.7, 2.15), (21.6, 2.15), cor=CIANO)
    rotulo(ax, 21.15, 2.65, "broker", cor=CIANO, tam=8.5)

    ax.text(0.4, 0.0, "Borda escura: plataforma (conhece o ESP-IDF).   "
            "Borda ciano: núcleo portável em C99, compila e é testado no PC.",
            fontsize=9, color=MUTED, va="top")
    salvar(fig, "arquitetura_c.png")


# ---------------------------------------------------------------- versão da aula

def fig_python():
    """Os 4 arquivos da aula e o equivalente em C de cada um."""
    fig, ax = nova_figura(21.0, 5.4)

    zona(ax, 0.2, 0.3, 20.6, 5.0, "sensor.py: liga tudo (thread de captura, fila limitada, laço de análise)",
         CIANO, CIANO_BG)

    y, h, w = 2.3, 2.0, 3.6
    bloco(ax, 0.7, y, w, h, "captura.py", "Scapy: ao vivo\nou arquivo .pcap", NAVY)
    bloco(ax, 5.9, y, 2.6, h, "fila", "queue.Queue\n(maxsize)", CINZA)
    bloco(ax, 10.1, y, w, h, "protocolos.py", "Evento\nModbus e S7comm", NAVY)
    bloco(ax, 15.3, y, w, h, "regras.py", "alertas\nestatísticas", NAVY)

    seta(ax, (4.3, y + h / 2), (5.9, y + h / 2))
    seta(ax, (8.5, y + h / 2), (10.1, y + h / 2))
    seta(ax, (13.7, y + h / 2), (15.3, y + h / 2))
    rotulo(ax, 5.1, y + h / 2 + 0.45, "IP, portas,\npayload", tam=8)
    rotulo(ax, 14.5, y + h / 2 + 0.45, "Evento", tam=8)
    seta(ax, (18.9, y + h / 2), (20.6, y + h / 2))
    rotulo(ax, 19.75, y + h / 2 + 0.55, "tela, CSV\n(MQTT)", tam=8)

    em_c = [
        (0.7 + w / 2, "em C: eth_cap\npool, parse_l2l4"),
        (5.9 + 1.3, "em C: fila do\nFreeRTOS"),
        (10.1 + w / 2, "em C: event_t\nproto_modbus, proto_s7"),
        (15.3 + w / 2, "em C: rules, stats\nassets, uplink_mqtt"),
    ]
    for cx, txt in em_c:
        ax.text(cx, 1.9, txt, ha="center", va="top", fontsize=8.5,
                color=AMBAR, fontstyle="italic", linespacing=1.3)

    salvar(fig, "pipeline_python.png")


if __name__ == "__main__":
    fig_implantacao()
    fig_arquitetura_c()
    fig_python()
