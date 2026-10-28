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
