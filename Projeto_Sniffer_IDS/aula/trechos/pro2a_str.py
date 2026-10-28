    def __str__(self):
        return (f"{self.origem:>15} -> {self.destino:<15} "
                f"{self.protocolo:6} {self.direcao:8} {self.operacao:9}"
                f" f={self.funcao:#04x} {self.area} end={self.endereco}"
                f" qtd={self.quantidade} {self.valores}"
                f" status={self.status:#06x}")
