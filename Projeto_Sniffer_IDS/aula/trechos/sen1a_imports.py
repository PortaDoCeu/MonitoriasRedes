import argparse
import queue
import threading
import time
from collections import Counter

from captura import capturar, ler_arquivo
from protocolos import decodificar
from regras import Janela, avaliar

contadores = Counter()
fila = queue.Queue(maxsize=1000)    # em C: xQueueCreate(1000, ...)
