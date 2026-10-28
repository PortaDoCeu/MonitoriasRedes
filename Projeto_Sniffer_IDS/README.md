# Sensor Passivo de Tráfego Industrial

Um sensor que escuta a rede, decodifica Modbus TCP e S7comm à mão e avisa quando algo foge do esperado. A arquitetura completa, incluindo a versão real em C para ESP32, está em [Arquitetura.md](Arquitetura.md).

## Estrutura

```
sensor/                    o que a turma escreve em sala
  captura.py               etapa 1: Scapy captura ao vivo ou lê .pcap -> Segmento
  protocolos.py            etapas 2 e 3: Evento, Modbus TCP e S7comm decodificados com struct
  regras.py                etapa 4: inventário, regras, janela de estatísticas
  sensor.py                etapa 5: thread de captura, fila limitada, laço de análise
ferramentas/
  mensagens.py             mensagens Modbus e S7 montadas byte a byte
  gerar_pcap.py            gera exemplo.pcap (cenário da aula) e carga.pcap (teste de limite)
  gerar_trafego.py         conversa com um CLP real por Modbus e S7, para o sensor capturar
testes/
  test_protocolos.py       testes dos decodificadores e das regras
```

## Preparar o PC

1. Instale o Python 3.12 e o **Npcap** (o instalador do Wireshark já traz o Npcap).
2. Na pasta `Projeto_Sniffer_IDS`, crie o ambiente e instale o Scapy:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Confira com os testes (não precisam de rede):
   ```
   python -m unittest discover -s testes -v
   ```

## Rodar

**Com o arquivo de exemplo** (funciona em qualquer PC, sem administrador):

```
cd ferramentas
python gerar_pcap.py
cd ..\sensor
python sensor.py --arquivo ..\exemplo.pcap
```

**Ao vivo na bancada** (terminal **como administrador**):

1. Ajuste os IPs em `sensor/regras.py` (`ATIVOS`) para os da bancada.
2. Num terminal, gere tráfego com o CLP da sua bancada:
   ```
   cd ferramentas
   python gerar_trafego.py --clp 192.168.0.11
   ```
3. Em outro terminal, como administrador, rode o sensor na placa ligada aos CLPs:
   ```
   cd sensor
   python sensor.py --interface "Ethernet"
   ```
   O nome da placa aparece em `Get-NetAdapter` no PowerShell.

**Medir o limite do Python:**

```
cd ferramentas
python gerar_pcap.py --carga 100000
cd ..\sensor
python sensor.py --arquivo ..\carga.pcap --quieto --medir
```

Num notebook comum, o resultado fica na casa de alguns milhares de segmentos por segundo. Uma rede de 100 Mbit pode entregar até cerca de 148 mil quadros por segundo.

## Saídas

- Na tela: cada evento decodificado, os alertas (`!!!`) e, a cada 10 s, o resumo da janela.
- `alertas.csv`: um alerta por linha, na pasta onde o sensor rodou.
- No fim (Ctrl+C ou fim do arquivo): contadores de capturados, eventos, não decodificados, descartados e alertas.

## Segurança na bancada

- O sensor só escuta. Quem gera tráfego é o `gerar_trafego.py`, e ele só **lê** do CLP.
- `gerar_trafego.py --escrever` faz **uma** escrita Modbus, para demonstrar o alerta R01. Use um registrador de teste, nunca um que comande uma saída do CLP.
- Capturas da bancada contêm valores do processo: não publique sem anonimizar.
