"""Figuras do documento de arquitetura (Projeto_Planta_MQTT).

Gera os PNGs em img/. Para mudar uma figura, edite a função e rode de novo:

    python figuras.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Ellipse, Rectangle

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
VERDE = "#2F855A"
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


def bloco(ax, x, y, w, h, titulo, sub="", cor=NAVY, nivel=None, nivel_dx=0.0):
    """Caixa branca com título em negrito e subtítulo (tecnologia)."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor="white", edgecolor=cor, linewidth=2, zorder=2))
    cx = x + w / 2
    if sub:
        ax.text(cx, y + h * 0.66, titulo, ha="center", va="center", fontsize=11,
                fontweight="bold", color=NAVY, zorder=3)
        ax.text(cx, y + h * 0.33, sub, ha="center", va="center", fontsize=8.5,
                color=MUTED, zorder=3, linespacing=1.3)
    else:
        ax.text(cx, y + h / 2, titulo, ha="center", va="center", fontsize=11,
                fontweight="bold", color=NAVY, zorder=3)
    if nivel is not None:
        ax.text(cx + nivel_dx, y - 0.25, f"Purdue nível {nivel}", ha="center", va="top",
                fontsize=8, color=cor, fontstyle="italic")


def cilindro(ax, x, y, w, h, titulo, sub="", cor=NAVY):
    """Banco de dados."""
    e = 0.3
    ax.add_patch(Rectangle((x, y + e / 2), w, h - e, facecolor="white",
                           edgecolor="none", zorder=2))
    ax.plot([x, x], [y + e / 2, y + h - e / 2], color=cor, lw=2, zorder=3)
    ax.plot([x + w, x + w], [y + e / 2, y + h - e / 2], color=cor, lw=2, zorder=3)
    ax.add_patch(Ellipse((x + w / 2, y + e / 2), w, e, facecolor="white",
                         edgecolor=cor, lw=2, zorder=2))
    ax.add_patch(Rectangle((x, y + e / 2), w, 0.02, facecolor="white",
                           edgecolor="none", zorder=2))
    ax.add_patch(Ellipse((x + w / 2, y + h - e / 2), w, e, facecolor="white",
                         edgecolor=cor, lw=2, zorder=3))
    ax.text(x + w / 2, y + h * 0.45, titulo, ha="center", va="center",
            fontsize=11, fontweight="bold", color=NAVY, zorder=4)
    if sub:
        ax.text(x + w / 2, y + h * 0.22, sub, ha="center", va="center",
                fontsize=8.5, color=MUTED, zorder=4)


def seta(ax, p1, p2, dupla=False, cor=INK, tracejada=False, lw=1.8):
    estilo = "<|-|>" if dupla else "-|>"
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=estilo, mutation_scale=14,
                                 color=cor, lw=lw, zorder=1,
                                 linestyle="--" if tracejada else "-"))


def linha(ax, pontos, cor=INK, lw=1.8):
    xs, ys = zip(*pontos)
    ax.plot(xs, ys, color=cor, lw=lw, zorder=1, solid_capstyle="round")


def caminho(ax, pontos, dupla=True, cor=INK):
    """Linha com cotovelos; a seta fica só no último segmento (e no primeiro, se dupla)."""
    if len(pontos) > 2:
        linha(ax, pontos[1:-1], cor=cor)
    seta(ax, pontos[-2], pontos[-1], cor=cor)
    if dupla:
        seta(ax, pontos[1], pontos[0], cor=cor)


def rotulo(ax, x, y, texto, cor=INK, tam=9, **kw):
    ax.text(x, y, texto, ha="center", va="center", fontsize=tam, color=cor,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor="none", alpha=0.95), zorder=5, **kw)


def salvar(fig, nome):
    fig.savefig(PASTA / nome, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("gerado:", PASTA / nome)


# ---------------------------------------------------------------- arquitetura

def fig_arquitetura():
    fig, ax = nova_figura(21.4, 7.2)

    zona(ax, 0.2, 0.3, 9.7, 6.6, "Zona OT (planta)", AMBAR, AMBAR_BG)
    zona(ax, 10.2, 0.3, 3.1, 6.6, "Conduto", CINZA, CINZA_BG)
    zona(ax, 13.6, 0.3, 7.6, 6.6, "Zona TI (aplicação)", CIANO, CIANO_BG)

    yb, hb = 2.4, 1.5
    bloco(ax, 0.5, yb, 2.0, hb, "Planta", "termopar\ninversor, motor", AMBAR, "0")
    bloco(ax, 3.9, yb, 2.0, hb, "CLP", "S7-1200\nMB_SERVER", AMBAR, "1")
    bloco(ax, 7.5, yb, 2.1, hb, "gateway.py", "pymodbus\npaho-mqtt", AMBAR, "2")
    bloco(ax, 10.6, yb, 2.3, hb, "Broker", "Mosquitto", CINZA, "3.5")
    bloco(ax, 14.6, yb, 2.6, hb, "middleware.py", "paho-mqtt\nFastAPI", CIANO, "4", nivel_dx=-0.8)
    cilindro(ax, 15.7, 0.55, 1.4, 1.3, "SQLite")
    bloco(ax, 18.6, 4.4, 2.2, 1.4, "App web", "navegador\ndo celular", CIANO, "4")

    ym = yb + hb / 2
    seta(ax, (2.5, ym), (3.9, ym), dupla=True)
    rotulo(ax, 3.2, ym + 0.45, "4-20 mA\ndigital", tam=8.5)

    seta(ax, (5.9, ym), (7.5, ym), dupla=True)
    rotulo(ax, 6.7, ym + 0.45, "Modbus TCP\n:502", tam=8.5)

    seta(ax, (9.6, ym), (10.6, ym), dupla=True)
    rotulo(ax, 10.1, ym - 0.5, "MQTT\n:1883", tam=8.5)

    seta(ax, (12.9, ym), (14.6, ym), dupla=True)
    rotulo(ax, 13.75, ym + 0.45, "MQTT\n:1883", tam=8.5)

    caminho(ax, [(11.75, yb + hb), (11.75, 5.1), (18.6, 5.1)])
    rotulo(ax, 15.3, 5.1, "MQTT sobre WebSocket  :9001", tam=8.5)

    caminho(ax, [(17.2, ym), (19.7, ym), (19.7, 4.4)])
    rotulo(ax, 19.0, ym - 0.35, "HTTP :8000", tam=8.5)

    seta(ax, (16.4, yb), (16.4, 1.85), dupla=True)

    ax.text(4.9, 0.7, "Só o gateway.py acessa a porta 502 do CLP",
            ha="center", fontsize=9.5, color=VERMELHO, fontweight="bold")

    salvar(fig, "arquitetura.png")


# ---------------------------------------------------------------- sequência

def sequencia(nome, participantes, passos, largura_col=3.4, passo_y=0.85):
    """Diagrama de sequência.

    participantes: lista de (chave, rótulo, cor).
    passos: ("msg", de, para, texto) | ("resp", de, para, texto)
            ("self", quem, texto) | ("faixa", texto, cor)
    """
    n = len(participantes)
    largura = n * largura_col + 1.0
    altura = (len(passos) + 1.2) * passo_y + 1.2
    fig, ax = nova_figura(largura, altura)

    xs = {}
    topo = altura - 0.3
    for i, (chave, texto, cor) in enumerate(participantes):
        x = 0.5 + largura_col * (i + 0.5)
        xs[chave] = x
        bloco(ax, x - 1.25, topo - 0.8, 2.5, 0.8, texto, cor=cor)
        ax.plot([x, x], [0.3, topo - 0.8], color=MUTED, lw=1.2,
                linestyle=(0, (4, 3)), zorder=0)

    y = topo - 0.8 - passo_y
    for p in passos:
        tipo = p[0]
        if tipo in ("msg", "resp"):
            _, a, b, texto = p
            seta(ax, (xs[a], y), (xs[b], y), tracejada=(tipo == "resp"),
                 cor=INK if tipo == "msg" else MUTED)
            ax.text((xs[a] + xs[b]) / 2, y + 0.12, texto, ha="center", va="bottom",
                    fontsize=9, color=INK, zorder=4,
                    bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="none"))
        elif tipo == "self":
            _, a, texto = p
            x = xs[a]
            linha(ax, [(x, y + 0.2), (x + 0.5, y + 0.2), (x + 0.5, y - 0.2)])
            seta(ax, (x + 0.5, y - 0.2), (x + 0.02, y - 0.2))
            ax.text(x + 0.65, y, texto, ha="left", va="center", fontsize=9, color=INK)
        elif tipo == "faixa":
            _, texto, cor = p
            ax.plot([0.4, largura - 0.4], [y + 0.25, y + 0.25], color=cor, lw=1.2)
            ax.text(0.5, y, texto, ha="left", va="center", fontsize=9,
                    fontweight="bold", color=cor,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=cor))
        y -= passo_y

    salvar(fig, nome)


def fig_telemetria():
    sequencia("fluxo_telemetria.png",
              [("clp", "CLP", AMBAR), ("gw", "gateway.py", AMBAR),
               ("b", "Broker", CINZA), ("app", "App", CIANO),
               ("mw", "middleware.py", CIANO)],
              [("faixa", "repete a cada 1 s", CIANO),
               ("msg", "gw", "clp", "FC 3: lê HR0 a HR9"),
               ("resp", "clp", "gw", "valores brutos"),
               ("self", "gw", "escala + timestamp"),
               ("msg", "gw", "b", "publica telemetria"),
               ("msg", "b", "app", "entrega (ao vivo)"),
               ("msg", "b", "mw", "entrega"),
               ("self", "mw", "grava em medicoes")])


def fig_comando():
    sequencia("fluxo_comando.png",
              [("app", "App", CIANO), ("b", "Broker", CINZA),
               ("gw", "gateway.py", AMBAR), ("clp", "CLP", AMBAR),
               ("mw", "middleware.py", CIANO)],
              [("msg", "app", "b", "publica comando"),
               ("msg", "b", "gw", "entrega"),
               ("msg", "b", "mw", "entrega (grava no log)"),
               ("self", "gw", "valida faixa e modo"),
               ("faixa", "se válido", VERDE),
               ("msg", "gw", "clp", "FC 6: escreve HR10"),
               ("resp", "clp", "gw", "eco da escrita"),
               ("msg", "gw", "b", "resposta: executado"),
               ("faixa", "se fora da faixa ou em modo local", VERMELHO),
               ("msg", "gw", "b", "resposta: rejeitado + motivo"),
               ("faixa", "nos dois casos", CINZA),
               ("msg", "b", "app", "entrega a resposta"),
               ("msg", "b", "mw", "atualiza o log")])


# ---------------------------------------------------------------- Purdue

def fig_purdue():
    fig, ax = nova_figura(15.5, 8.4)
    niveis = [
        ("4", "Negócio / aplicação", ["middleware.py", "SQLite", "App web"], CIANO, CIANO_BG),
        ("3.5", "DMZ industrial", ["Broker Mosquitto"], CINZA, CINZA_BG),
        ("2", "Supervisão", ["gateway.py"], AMBAR, AMBAR_BG),
        ("1", "Controle", ["CLP S7-1200"], AMBAR, AMBAR_BG),
        ("0", "Processo", ["Termopar", "Inversor", "Motor"], AMBAR, AMBAR_BG),
    ]
    h, gap = 1.3, 0.25
    y = 8.0
    for nivel, nome, itens, cor, fundo in niveis:
        y -= h
        ax.add_patch(FancyBboxPatch((0.2, y), 12.6, h, boxstyle="round,pad=0,rounding_size=0.12",
                                    facecolor=fundo, edgecolor=cor, lw=1.5, zorder=0))
        ax.text(0.5, y + h * 0.62, f"Nível {nivel}", fontsize=12, fontweight="bold",
                color=cor, va="center")
        ax.text(0.5, y + h * 0.3, nome, fontsize=9, color=MUTED, va="center")
        wi = 2.7
        x0 = 3.6
        for i, item in enumerate(itens):
            bloco(ax, x0 + i * (wi + 0.35), y + 0.25, wi, h - 0.5, item, cor=cor)
        y -= gap

    def chave(y0, y1, texto, cor):
        x = 13.1
        linha(ax, [(x, y0), (x + 0.25, y0), (x + 0.25, y1), (x, y1)], cor=cor, lw=2)
        ax.text(x + 0.45, (y0 + y1) / 2, texto, fontsize=11, fontweight="bold",
                color=cor, va="center")

    topo = 8.0
    chave(topo, topo - h, "TI", CIANO)
    chave(topo - h - gap, topo - 2 * h - gap, "Conduto", CINZA)
    chave(topo - 2 * (h + gap), topo - 5 * h - 4 * gap, "OT", AMBAR)

    salvar(fig, "purdue.png")


# ---------------------------------------------------------------- contrato de dados

def fig_contrato():
    fig, ax = nova_figura(19.0, 10.6)

    # linhas da tabela de registradores (y do centro de cada linha)
    h = 0.72
    linhas = [
        ("HR0", "Temperatura (°C × 10)", "leitura"),
        ("HR1", "Velocidade real (rpm)", "leitura"),
        ("HR2", "Palavra de status", "leitura"),
        ("HR3", "Referência em uso (rpm)", "leitura"),
        ("HR4", "Código de falha", "leitura"),
        ("HR5 a HR9", "reservados", "reservado"),
        (None, None, None),
        ("HR10", "Referência de velocidade", "escrita"),
        ("HR11", "Comando do motor", "escrita"),
        ("HR12", "Heartbeat", "escrita"),
        ("HR13 a HR19", "reservados", "reservado"),
    ]
    cores = {"leitura": (AMBAR, AMBAR_BG), "escrita": (CIANO, CIANO_BG),
             "reservado": (CINZA, "white")}
    y = 9.3
    ys = {}
    for reg, nome, tipo in linhas:
        if reg is None:
            y -= 0.5
            continue
        cor, fundo = cores[tipo]
        ax.add_patch(Rectangle((0.5, y - h / 2), 5.2, h, facecolor=fundo,
                               edgecolor=cor, lw=1.4, zorder=2))
        estilo = "italic" if tipo == "reservado" else "normal"
        ax.text(0.7, y, reg, fontsize=10, fontweight="bold", color=cor, va="center", zorder=3)
        ax.text(2.75 if tipo == "reservado" else 2.35, y, nome, fontsize=9.5, color=INK if tipo != "reservado" else MUTED,
                va="center", fontstyle=estilo, zorder=3)
        ys[reg] = y
        y -= h

    ax.text(3.1, 9.3 + 0.8, "CLP: holding registers", ha="center", fontsize=11,
            fontweight="bold", color=NAVY)
    ax.text(0.5, ys["HR0"] + 0.45, "área de leitura", fontsize=8.5, color=AMBAR,
            fontstyle="italic")
    ax.text(0.5, ys["HR10"] + 0.45, "área de escrita", fontsize=8.5, color=CIANO,
            fontstyle="italic")

    # faixa do gateway
    ax.add_patch(FancyBboxPatch((7.6, 0.4), 2.6, 9.9, boxstyle="round,pad=0,rounding_size=0.2",
                                facecolor=CINZA_BG, edgecolor=CINZA, lw=1.4,
                                linestyle=(0, (5, 3)), zorder=0))
    ax.text(8.9, 10.0, "gateway.py", ha="center", fontsize=11, fontweight="bold", color=NAVY)
    ax.text(8.9, 0.75, "escala, bits → JSON\nvalidação, timestamp", ha="center",
            fontsize=8.5, color=MUTED, linespacing=1.4)

    # tópicos
    xt, wt = 12.2, 6.3
    topicos = [
        ("telemetria/temperatura", ys["HR0"], AMBAR, ["HR0"]),
        ("telemetria/velocidade", ys["HR1"], AMBAR, ["HR1"]),
        ("telemetria/referencia", ys["HR3"], AMBAR, ["HR3"]),
        ("telemetria/status  (retido)", ys["HR4"], AMBAR, ["HR4", "HR2"]),
        ("comando/velocidade", ys["HR10"], CIANO, ["HR10"]),
        ("comando/motor", ys["HR11"], CIANO, ["HR11"]),
        ("comando/resposta", ys["HR12"], CINZA, []),
        ("gateway/estado  (retido, Last Will)", ys["HR13 a HR19"], CINZA, []),
    ]
    ax.text(xt + wt / 2, 9.3 + 0.8, "Broker: tópicos bancada1/...", ha="center",
            fontsize=11, fontweight="bold", color=NAVY)
    for nome, yt, cor, regs in topicos:
        ax.add_patch(FancyBboxPatch((xt, yt - 0.28), wt, 0.56,
                                    boxstyle="round,pad=0,rounding_size=0.1",
                                    facecolor="white", edgecolor=cor, lw=1.6, zorder=2))
        ax.text(xt + 0.2, yt, nome, fontsize=9.5, family="DejaVu Sans Mono",
                color=INK, va="center", zorder=3)
        for r in regs:
            yr = ys[r]
            if cor == CIANO:   # comando: tópico → registrador
                seta(ax, (xt, yt), (5.7, yr), cor=cor)
            elif r == "HR2":   # status junta HR2 e HR4: HR2 desce com cotovelo
                linha(ax, [(5.7, yr), (6.6, yr), (6.6, yt + 0.12)], cor=cor)
                seta(ax, (6.6, yt + 0.12), (xt, yt + 0.12), cor=cor)
            elif r == "HR4":
                seta(ax, (5.7, yr - 0.12), (xt, yt - 0.12), cor=cor)
            else:              # telemetria: registrador → tópico
                seta(ax, (5.7, yr), (xt, yt), cor=cor)
        if not regs:           # gerado pelo próprio gateway
            seta(ax, (10.2, yt), (xt, yt), cor=cor)

    # heartbeat: nasce no gateway e vai só para o CLP
    seta(ax, (7.6, ys["HR12"]), (5.7, ys["HR12"]), cor=CIANO)
    ax.text(6.65, ys["HR12"] + 0.2, "contador", ha="center", fontsize=8.5, color=CIANO)

    salvar(fig, "contrato.png")


# ---------------------------------------------------------------- rede da bancada

def fig_rede():
    fig, ax = nova_figura(20.0, 9.2)
    zona(ax, 0.2, 0.3, 19.6, 8.6, "Sub-rede 192.168.0.0/24, sem rota para a internet",
         CINZA, "#F7F8FA")

    bloco(ax, 0.8, 5.2, 3.0, 1.5, "CLP S7-1200", "192.168.0.1\nMB_SERVER :502", AMBAR)
    bloco(ax, 8.4, 5.45, 2.4, 1.0, "Switch", cor=CINZA)
    bloco(ax, 13.6, 5.2, 2.6, 1.5, "AP Wi-Fi", "192.168.0.2\nWPA2, DHCP", CINZA)

    # celulares
    for i, y in enumerate([6.6, 5.3, 4.0]):
        bloco(ax, 17.6, y, 1.8, 0.95, "Celular", f".10{i}", CIANO)
    ax.text(18.5, 3.55, "DHCP .100 a .199", ha="center", fontsize=8.5, color=MUTED)

    # notebook com os serviços
    x, y, w, h = 4.6, 0.8, 10.6, 3.2
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor="white", edgecolor=NAVY, lw=2, zorder=2))
    ax.text(x + 0.3, y + h - 0.35, "Notebook  192.168.0.10  (cabo)", fontsize=11,
            fontweight="bold", color=NAVY, va="top", zorder=3)
    servicos = [
        ("gateway.py", "cliente Modbus → CLP :502", AMBAR),
        ("Mosquitto", ":1883 só 127.0.0.1   |   :9001 WebSocket", CINZA),
        ("middleware.py", ":8000 HTTP   |   SQLite local", CIANO),
    ]
    for i, (nome, desc, cor) in enumerate(servicos):
        yy = y + h - 1.05 - i * 0.62
        ax.add_patch(Rectangle((x + 0.3, yy - 0.22), 0.12, 0.44, facecolor=cor,
                               edgecolor="none", zorder=3))
        ax.text(x + 0.6, yy, nome, fontsize=10, fontweight="bold", color=NAVY,
                va="center", zorder=3)
        ax.text(x + 3.1, yy, desc, fontsize=9.5, color=INK, va="center", zorder=3,
                family="DejaVu Sans Mono")
    ax.text(x + w - 0.3, y + 0.3, "Firewall: entrada só 8000 e 9001, origem 192.168.0.0/24",
            ha="right", fontsize=9, color=VERMELHO, fontweight="bold", zorder=3)

    # cabos (físico)
    seta(ax, (3.8, 5.95), (8.4, 5.95), dupla=True, cor=INK)
    rotulo(ax, 6.1, 6.35, "cabo  (Modbus TCP :502)", tam=8.5, cor=AMBAR)
    seta(ax, (10.8, 5.95), (13.6, 5.95), dupla=True, cor=INK)
    rotulo(ax, 12.2, 6.35, "cabo", tam=8.5)
    seta(ax, (9.6, 5.45), (9.6, 4.0), dupla=True, cor=INK)
    rotulo(ax, 10.25, 4.72, "cabo", tam=8.5)

    # Wi-Fi
    for yc in [7.07, 5.77, 4.47]:
        seta(ax, (16.2, 5.95), (17.6, yc), dupla=True, cor=CIANO, tracejada=True, lw=1.4)
    rotulo(ax, 16.6, 7.6, "Wi-Fi: HTTP :8000\nMQTT/WS :9001", tam=8.5, cor=CIANO)

    salvar(fig, "rede.png")


if __name__ == "__main__":
    fig_rede()
    fig_contrato()
    fig_arquitetura()
    fig_telemetria()
    fig_comando()
    fig_purdue()
