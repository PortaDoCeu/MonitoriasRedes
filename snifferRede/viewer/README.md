# Packet Viewer

Visualizador web simples e desacoplado do firmware.

## O que ele faz

- recebe `PUT /suspicious-packet`
- opcionalmente le JSON direto da serial
- guarda os pacotes mais recentes em memoria
- serve uma pagina web em `/`
- expõe a lista em `GET /api/packets`

## Como rodar

Na raiz do projeto:

```powershell
python viewer/server.py --host 0.0.0.0 --port 8080
```

Depois abra:

```text
http://SEU_IP:8080/
```

Nao abra `viewer/static/index.html` direto no navegador via `file://`.
Abra sempre pela URL do servidor HTTP acima.

## Modo serial

Se quiser alimentar a pagina sem HTTP, leia a UART do ESP32 diretamente:

```powershell
python viewer/server.py --host 0.0.0.0 --port 8080 --serial-port COM10 --serial-baud 115200
```

Nesse modo, o servidor tenta interpretar cada linha recebida na serial como JSON do sniffer.
Linhas que nao forem JSON valido sao ignoradas.

## Firmware

O endpoint atual do ESP32 precisa apontar para a maquina que roda este servidor:

```c
#define HTTP_ALERT_URL "http://192.168.0.200:8080/suspicious-packet"
```

Arquivo:

`main/src/app/l2tap_sniffer_main.c`
