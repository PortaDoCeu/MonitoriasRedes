"""Figuras da Aula 3 (switch gerenciado na rede da planta).

Gera os PNGs em img/. Para mudar uma figura, edite a função e rode de novo:

    python figuras.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

PASTA = Path(__file__).parent / "img"
PASTA.mkdir(exist_ok=True)

NAVY = "#111827"
INK = "#1F2937"
MUTED = "#5B6677"
CIANO = "#0B7F7D"
CIANO_BG = "#EAF6F6"
AMBAR = "#B7791F"
AMBAR_BG = "#FDF3E1"
ROXO = "#6B46C1"
ROXO_BG = "#F1EDFB"
CINZA = "#5B6677"
CINZA_BG = "#EEF0F4"
VERMELHO = "#C53030"
VERDE = "#2F855A"

# cor de cada célula
CELULAS = [("Grupo 1", "celula1 (10)", "1 a 8", CIANO, CIANO_BG),
           ("Grupo 2", "celula2 (20)", "9 a 16", AMBAR, AMBAR_BG),
           ("Grupo 3", "celula3 (30)", "17 a 24", ROXO, ROXO_BG)]

plt.rcParams["font.family"] = "DejaVu Sans"


# ---------------------------------------------------------------- peças

def nova_figura(largura, altura, escala=0.75):
    fig, ax = plt.subplots(figsize=(largura * escala, altura * escala))
    ax.set_xlim(0, largura)
    ax.set_ylim(0, altura)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def zona(ax, x, y, w, h, titulo, cor, fundo, tam=11):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.2",
                                facecolor=fundo, edgecolor=cor, linewidth=1.6,
                                linestyle=(0, (5, 3)), zorder=0))
    ax.text(x + 0.2, y + h - 0.25, titulo, color=cor, fontsize=tam, fontweight="bold",
            va="top", ha="left")


def bloco(ax, x, y, w, h, titulo, sub="", cor=NAVY, tam=10.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                facecolor="white", edgecolor=cor, linewidth=2, zorder=2))
    cx = x + w / 2
    if sub:
        ax.text(cx, y + h * 0.66, titulo, ha="center", va="center", fontsize=tam,
                fontweight="bold", color=NAVY, zorder=3)
        ax.text(cx, y + h * 0.3, sub, ha="center", va="center", fontsize=tam - 2.5,
                color=MUTED, zorder=3, linespacing=1.25)
    else:
        ax.text(cx, y + h / 2, titulo, ha="center", va="center", fontsize=tam,
                fontweight="bold", color=NAVY, zorder=3)


def seta(ax, p1, p2, dupla=False, cor=INK, tracejada=False, lw=1.8):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="<|-|>" if dupla else "-|>",
                                 mutation_scale=13, color=cor, lw=lw, zorder=1,
                                 linestyle="--" if tracejada else "-"))


def linha(ax, pontos, cor=INK, lw=1.8, tracejada=False):
    xs, ys = zip(*pontos)
    ax.plot(xs, ys, color=cor, lw=lw, zorder=1, linestyle="--" if tracejada else "-")


def rotulo(ax, x, y, texto, cor=INK, tam=9, **kw):
    ax.text(x, y, texto, ha="center", va="center", fontsize=tam, color=cor,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.95),
            zorder=5, **kw)


def salvar(fig, nome):
    fig.savefig(PASTA / nome, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("gerado:", PASTA / nome)


# ---------------------------------------------------------------- topologia

def fig_topologia():
    fig, ax = nova_figura(20.0, 11.0)

    # switch no centro
    ax.add_patch(FancyBboxPatch((1.0, 4.6), 18.0, 1.8, boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor=NAVY, edgecolor=NAVY, zorder=2))
    ax.text(1.4, 6.1, "Switch ExtremeXOS 21.1", color="white", fontsize=12,
            fontweight="bold", va="top", zorder=3)
    # blocos de portas
    blocos = [(2.0, "1 a 8", CIANO), (6.0, "9 a 16", AMBAR), (10.0, "17 a 24", ROXO),
              (14.0, "25 a 28", CINZA)]
    for x, txt, cor in blocos:
        ax.add_patch(Rectangle((x, 4.85), 3.4, 0.7, facecolor=cor, edgecolor="none", zorder=3))
        ax.text(x + 1.7, 5.2, f"portas {txt}", color="white", fontsize=9.5,
                fontweight="bold", ha="center", va="center", zorder=4)
    ax.add_patch(Rectangle((17.6, 4.85), 0.7, 0.7, facecolor=VERMELHO, edgecolor="none", zorder=3))
    ax.text(17.95, 5.2, "35", color="white", fontsize=9.5, fontweight="bold",
            ha="center", va="center", zorder=4)
    ax.add_patch(Rectangle((17.0, 5.75), 1.9, 0.45, facecolor="#374151", edgecolor="none", zorder=3))
    ax.text(17.95, 5.97, "MGMT", color="white", fontsize=8.5, fontweight="bold",
            ha="center", va="center", zorder=4)

    # células acima
    for i, (grupo, vlan, portas, cor, fundo) in enumerate(CELULAS):
        x = 0.6 + i * 4.6
        zona(ax, x, 7.0, 4.3, 3.6, f"Célula {i + 1}: {grupo}", cor, fundo, tam=10)
        bloco(ax, x + 0.25, 7.5, 1.8, 1.4, f"CLP {i + 1}A", f"192.168.0.{(i + 1) * 10 + 1}", cor)
        bloco(ax, x + 2.25, 7.5, 1.8, 1.4, f"CLP {i + 1}B", f"192.168.0.{(i + 1) * 10 + 2}", cor)
        ax.text(x + 2.15, 9.6, f"VLAN {vlan}", ha="center", fontsize=8.5, color=cor)
        linha(ax, [(x + 1.15, 7.5), (x + 1.15, 7.0)], cor=cor)
        linha(ax, [(x + 3.15, 7.5), (x + 3.15, 7.0)], cor=cor)
        seta(ax, (x + 2.15, 7.0), (2.0 + i * 4.0 + 1.7, 5.6), dupla=True, cor=cor)

    # supervisão acima à direita
    zona(ax, 14.4, 7.0, 5.0, 3.6, "Supervisão", CINZA, CINZA_BG, tam=10)
    bloco(ax, 14.7, 7.5, 2.0, 1.4, "CLP 7", "192.168.0.70", CINZA)
    bloco(ax, 17.0, 7.5, 2.1, 1.4, "Monitor", "192.168.0.200", CINZA)
    ax.text(16.9, 9.6, "VLAN supervisao (70)", ha="center", fontsize=8.5, color=CINZA)
    seta(ax, (16.9, 7.0), (15.7, 5.6), dupla=True, cor=CINZA)

    # notebooks abaixo
    for i, (grupo, vlan, portas, cor, fundo) in enumerate(CELULAS):
        x = 0.6 + i * 4.6
        bloco(ax, x + 0.6, 2.2, 3.1, 1.3, f"Notebooks {grupo}", f"192.168.0.{101 + i * 10} a .{104 + i * 10}", cor, tam=9.5)
        seta(ax, (x + 2.15, 3.5), (2.0 + i * 4.0 + 1.7, 4.85), dupla=True, cor=cor)

    # estação de captura e gerência
    bloco(ax, 14.4, 2.2, 2.6, 1.3, "Captura", "porta 35, Wireshark", VERMELHO, tam=9.5)
    seta(ax, (17.95, 4.85), (15.7, 3.5), cor=VERMELHO)
    rotulo(ax, 17.6, 4.2, "cópia (mirror)", cor=VERMELHO, tam=8.5)
    bloco(ax, 17.3, 2.2, 2.3, 1.3, "Gerência", "192.168.1.10\nSSH", "#374151", tam=9.5)
    seta(ax, (18.4, 3.5), (18.0, 5.75), dupla=True, cor="#374151")

    ax.text(10, 1.2, "Todos os CLPs na faixa 192.168.0.0/24: quem separa as células é a VLAN, não o IP.",
            ha="center", fontsize=10, color=VERMELHO, fontweight="bold")
    salvar(fig, "topologia.png")


# ---------------------------------------------------------------- aprendizado de MAC

def fig_aprendizado():
    fig, ax = nova_figura(19.0, 8.6)

    def cena(x0, titulo, destaque_porta, fdb, enviar_para, nota):
        zona(ax, x0, 0.4, 8.9, 7.8, titulo, NAVY, "#F7F8FA", tam=10.5)
        ax.add_patch(FancyBboxPatch((x0 + 2.9, 3.6), 3.1, 1.4, boxstyle="round,pad=0,rounding_size=0.12",
                                    facecolor=NAVY, edgecolor=NAVY, zorder=2))
        ax.text(x0 + 4.45, 4.3, "switch", color="white", fontsize=10.5, fontweight="bold",
                ha="center", va="center", zorder=3)
        equipamentos = [("A", "porta 1", x0 + 0.5, 5.6), ("B", "porta 2", x0 + 6.6, 5.6),
                        ("C", "porta 3", x0 + 0.5, 1.4), ("D", "porta 4", x0 + 6.6, 1.4)]
        for nome, porta, x, y in equipamentos:
            cor = VERMELHO if nome == destaque_porta else NAVY
            bloco(ax, x, y, 1.8, 1.1, nome, porta, cor, tam=10)
            cx, cy = x + 0.9, y + (0 if y > 3 else 1.1)
            alvo = (x0 + 4.45 + (-0.9 if x < x0 + 4 else 0.9), 5.0 if y > 3 else 3.6)
            vai = nome in enviar_para
            seta(ax, alvo, (cx, cy), cor=VERDE if vai else RuleGray(), lw=2.2 if vai else 1.2,
                 tracejada=not vai)
        # tabela FDB
        ax.text(x0 + 4.45, 3.1, "tabela MAC (FDB)", ha="center", fontsize=8.5, color=MUTED,
                fontweight="bold")
        for k, (mac, porta) in enumerate(fdb):
            ax.text(x0 + 4.45, 2.65 - k * 0.42, f"{mac}  →  {porta}", ha="center", fontsize=8.5,
                    family="DejaVu Sans Mono", color=INK)
        if not fdb:
            ax.text(x0 + 4.45, 2.65, "(vazia)", ha="center", fontsize=8.5, color=MUTED)
        ax.text(x0 + 4.45, 0.75, nota, ha="center", fontsize=8.8, color=INK, linespacing=1.3)

    cena(0.2, "1. A manda para B; o switch ainda não conhece B", "A",
         [("MAC de A", "porta 1")], ["B", "C", "D"],
         "Aprende que A está na porta 1 e,\nsem saber onde está B, copia para todas (inundação).")
    cena(9.9, "2. B responde para A; agora ele sabe os dois", "B",
         [("MAC de A", "porta 1"), ("MAC de B", "porta 2")], ["A"],
         "Aprende que B está na porta 2 e entrega\nsó na porta 1. C e D não veem mais a conversa.")
    salvar(fig, "aprendizado_mac.png")


def RuleGray():
    return "#B8C0CC"


# ---------------------------------------------------------------- VLANs antes e depois

def fig_vlans():
    fig, ax = nova_figura(19.0, 7.6)

    def painel(x0, titulo, separado):
        zona(ax, x0, 0.3, 8.9, 7.0, titulo, NAVY, "#F7F8FA", tam=10.5)
        ax.add_patch(FancyBboxPatch((x0 + 0.5, 3.0), 7.9, 1.2, boxstyle="round,pad=0,rounding_size=0.12",
                                    facecolor=NAVY, edgecolor=NAVY, zorder=2))
        ax.text(x0 + 4.45, 3.6, "switch", color="white", fontsize=10.5, fontweight="bold",
                ha="center", va="center", zorder=3)
        for i, (grupo, vlan, portas, cor, fundo) in enumerate(CELULAS):
            x = x0 + 0.5 + i * 2.75
            c = cor if separado else MUTED
            f = fundo if separado else "#F3F4F6"
            ax.add_patch(FancyBboxPatch((x, 4.6), 2.4, 1.9, boxstyle="round,pad=0,rounding_size=0.12",
                                        facecolor=f, edgecolor=c, lw=1.6, zorder=1))
            ax.text(x + 1.2, 6.15, f"Célula {i + 1}", ha="center", fontsize=9.5, fontweight="bold", color=c)
            ax.text(x + 1.2, 5.6, "CLP A   CLP B", ha="center", fontsize=8.5, color=INK)
            ax.text(x + 1.2, 5.05, f"VLAN {vlan.split()[0]}" if separado else "VLAN default",
                    ha="center", fontsize=8.2, color=c)
            seta(ax, (x + 1.2, 4.6), (x + 1.2, 4.2), dupla=True, cor=c)
        if separado:
            for i in range(1, 3):
                xx = x0 + 0.5 + i * 2.75 - 0.18
                ax.plot([xx, xx], [2.9, 6.6], color=VERMELHO, lw=2.2, zorder=4)
            ax.text(x0 + 4.45, 1.8, "Três domínios de broadcast: um broadcast da célula 1\n"
                                    "só chega na célula 1. Entre células, nada passa.",
                    ha="center", fontsize=9, color=INK, linespacing=1.35)
        else:
            ax.annotate("", xy=(x0 + 7.9, 2.45), xytext=(x0 + 1.0, 2.45),
                        arrowprops=dict(arrowstyle="<|-|>", color=VERMELHO, lw=1.6))
            ax.text(x0 + 4.45, 1.55, "Um domínio de broadcast só: qualquer equipamento\n"
                                    "alcança qualquer CLP, de qualquer célula.",
                    ha="center", fontsize=9, color=INK, linespacing=1.35)
            ax.text(x0 + 4.45, 2.1, "broadcast chega em todas as portas", ha="center",
                    fontsize=8.2, color=VERMELHO)
        ax.text(x0 + 4.45, 0.75, "comandos: create vlan, configure vlan ... add ports" if separado
                else "configuração de fábrica: todas as portas na VLAN default",
                ha="center", fontsize=8.5, color=MUTED, family="DejaVu Sans Mono" if separado else None)

    painel(0.2, "Antes: rede plana", False)
    painel(9.9, "Depois: uma VLAN por célula", True)
    salvar(fig, "vlans.png")


# ---------------------------------------------------------------- espelhamento

def fig_espelhamento():
    fig, ax = nova_figura(16.0, 7.6)
    ax.add_patch(FancyBboxPatch((3.0, 3.0), 10.0, 1.6, boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor=NAVY, edgecolor=NAVY, zorder=2))
    ax.text(8.0, 3.8, "switch", color="white", fontsize=11, fontweight="bold",
            ha="center", va="center", zorder=3)
    bloco(ax, 1.0, 5.6, 2.6, 1.3, "CLP 1A", "porta 1 (origem)", CIANO)
    bloco(ax, 6.7, 5.6, 2.6, 1.3, "CLP 1B", "porta 2", CIANO)
    seta(ax, (2.3, 5.6), (4.2, 4.6), dupla=True, cor=CIANO, lw=2.2)
    seta(ax, (8.0, 5.6), (8.0, 4.6), dupla=True, cor=CIANO, lw=2.2)
    rotulo(ax, 5.2, 6.6, "PUT/GET (S7comm)", cor=CIANO, tam=9.5)
    bloco(ax, 10.6, 0.6, 3.6, 1.5, "Notebook de captura", "porta 35, Wireshark", VERMELHO)
    seta(ax, (11.8, 3.0), (12.4, 2.1), cor=VERMELHO, lw=2.4)
    rotulo(ax, 14.6, 2.55,"cópia de tudo que\npassa na porta 1", cor=VERMELHO, tam=9)
    bloco(ax, 1.0, 0.6, 3.4, 1.5, "Notebook do grupo", "porta 3: não vê nada", MUTED)
    seta(ax, (4.0, 3.0), (2.7, 2.1), cor=MUTED, tracejada=True)
    ax.text(8.0, 7.3, "configure mirror CAPTURA add port 1 ingress-and-egress", ha="center",
            fontsize=9.5, family="DejaVu Sans Mono", color=NAVY)
    salvar(fig, "espelhamento.png")


if __name__ == "__main__":
    fig_topologia()
    fig_aprendizado()
    fig_vlans()
    fig_espelhamento()
