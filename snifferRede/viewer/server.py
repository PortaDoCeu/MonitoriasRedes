from __future__ import annotations

import argparse
import json
import threading
from collections import deque
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import serial


MAX_PACKETS = 200
STATIC_DIR = Path(__file__).with_name("static")
PACKETS: deque[dict] = deque(maxlen=MAX_PACKETS)
PACKETS_LOCK = threading.Lock()
PACKET_SEQ = 0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_static_file(name: str) -> bytes:
    return (STATIC_DIR / name).read_bytes()


def json_bytes(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=True).encode("utf-8")


def next_packet_id() -> int:
    global PACKET_SEQ
    with PACKETS_LOCK:
        PACKET_SEQ += 1
        return PACKET_SEQ


def append_packet(packet: dict) -> None:
    with PACKETS_LOCK:
        PACKETS.appendleft(packet)


def list_packets() -> list[dict]:
    with PACKETS_LOCK:
        return list(PACKETS)


def ingest_packet(parsed_body: dict, source: str) -> dict:
    packet = {
        "id": next_packet_id(),
        "received_at": utc_now_iso(),
        "remote_addr": source,
        "packet": parsed_body,
    }
    append_packet(packet)
    return packet


def try_extract_json(line: str) -> dict | None:
    line = line.strip()
    if not line:
        return None

    candidates = [line]
    start = line.find("{")
    end = line.rfind("}")
    if (start >= 0) and (end > start):
        candidates.append(line[start:end + 1])

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, dict):
            return parsed

    return None


def serial_reader_loop(port: str, baud: int) -> None:
    source = f"serial:{port}"

    while True:
        try:
            with serial.Serial(port=port, baudrate=baud, timeout=1) as ser:
                print(f"Serial packet reader attached to {port} @ {baud} baud")
                while True:
                    raw_line = ser.readline()
                    if not raw_line:
                        continue

                    try:
                        line = raw_line.decode("utf-8", errors="ignore")
                    except UnicodeDecodeError:
                        continue

                    parsed = try_extract_json(line)
                    if parsed is None:
                        continue

                    packet = ingest_packet(parsed, source)
                    print(f"[serial] captured packet #{packet['id']} from {source}")
        except serial.SerialException as exc:
            print(f"Serial reader error on {port}: {exc}")
            threading.Event().wait(2.0)


class PacketViewerHandler(BaseHTTPRequestHandler):
    server_version = "PacketViewer/1.0"

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_common_headers()
        self.end_headers()

    def do_GET(self) -> None:
        route = urlparse(self.path).path

        if route == "/":
            self._serve_index()
            return

        if route == "/api/packets":
            self._serve_packets()
            return

        if route == "/healthz":
            self._send_json(HTTPStatus.OK, {"status": "ok", "packets": len(list_packets())})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_PUT(self) -> None:
        route = urlparse(self.path).path
        if route != "/suspicious-packet":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            parsed_body = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
            return

        packet = ingest_packet(parsed_body, self.client_address[0])

        self._send_json(HTTPStatus.ACCEPTED, {"status": "accepted", "id": packet["id"]})

    def log_message(self, format: str, *args) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = format % args
        print(f"[{timestamp}] {self.address_string()} {message}")

    def _serve_index(self) -> None:
        body = read_static_file("index.html")
        self.send_response(HTTPStatus.OK)
        self._send_common_headers()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_packets(self) -> None:
        packets = list_packets()
        self._send_json(
            HTTPStatus.OK,
            {
                "packets": packets,
                "count": len(packets),
                "max_packets": MAX_PACKETS,
                "server_time": utc_now_iso(),
            },
        )

    def _send_json(self, status: HTTPStatus, payload: object) -> None:
        body = json_bytes(payload)
        self.send_response(status)
        self._send_common_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_common_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple viewer for suspicious packets")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host, default: 0.0.0.0")
    parser.add_argument("--port", type=int, default=8080, help="Bind port, default: 8080")
    parser.add_argument("--serial-port", help="Optional serial port, for example COM10")
    parser.add_argument("--serial-baud", type=int, default=460800, help="Serial baud rate, default: 460800")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), PacketViewerHandler)
    print(f"Packet viewer listening on http://{args.host}:{args.port}")
    print("PUT suspicious packets to /suspicious-packet")
    if args.serial_port:
        serial_thread = threading.Thread(
            target=serial_reader_loop,
            args=(args.serial_port, args.serial_baud),
            daemon=True,
        )
        serial_thread.start()
        print(f"Serial ingestion enabled on {args.serial_port} @ {args.serial_baud}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
