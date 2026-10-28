import struct
from dataclasses import dataclass, field


@dataclass
class Evento:
    ts: float
    origem: str
    destino: str
    protocolo: str     # "modbus" ou "s7"
    direcao: str       # "pergunta" ou "resposta"
    operacao: str      # "leitura", "escrita", "controle", "outra"
    funcao: int        # código da função no protocolo
    area: str = ""
    endereco: int = 0
    quantidade: int = 0
    status: int = 0    # 0 = ok; senão, código de erro
    valores: list = field(default_factory=list)
