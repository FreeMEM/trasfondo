#!/usr/bin/env python3
"""Lanza tests/prueba_certificados.dash en el emulador (AmigaOS 3.2.3 con RTG, AmiSSL y la red del PC), con
build/trasfondo, build/trasfondoprefs y build/barra en DH0:. Levanta en el PC dos servidores HTTPS de prueba con
certificados autofirmados (los de las pruebas de Dash, tests/certs de FreeMEMLang): 127.0.0.1:44301 hace de la API de
GitHub (dice que la última es la 2.10.1) y 127.0.0.1:44302 de Open-Meteo. Las capturas quedan en
build/prueba_certificados/capturas/.

    DASH=~/Projects/FreeMEMLang PYTHONPATH=$DASH KS=kick323.rom flock /run/user/1000/dash-emu-red.lock \\
        python3 tests/prueba_certificados.py
"""

import json
import os
import shutil
import socketserver
import ssl
import sys
import threading
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
DASH = Path(os.environ["DASH"])
sys.path.insert(0, str(DASH / "tools"))
from emu_run import run_programs, MACHINES   # noqa: E402

GITHUB = json.dumps({"tag_name": "v2.10.1", "name": "Trasfondo 2.10.1", "body": "prueba", "assets": []}, separators=(",", ":"))
TIEMPO = json.dumps({"current": {"temperature_2m": 17.3, "weather_code": 1, "is_day": 1},
                     "daily": {"time": ["2026-11-24", "2026-11-25"], "weather_code": [1, 3],
                               "temperature_2m_max": [21.5, 19.0], "temperature_2m_min": [12.1, 11.0]}}, separators=(",", ":"))


class Respuesta(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            linea = self.rfile.readline().decode("latin-1")
            while self.rfile.readline() not in (b"\r\n", b"\n", b""):
                pass
            cuerpo = GITHUB if "/repos/" in linea else TIEMPO
            print("  servidor:", self.server.server_address[1], linea.strip(), flush=True)
            datos = cuerpo.encode()
            self.wfile.write(b"HTTP/1.0 200 OK\r\nContent-Type: application/json\r\nContent-Length: %d\r\n"
                             b"Connection: close\r\n\r\n" % len(datos) + datos)
        except (ssl.SSLError, OSError):
            pass


class ServidorTLS(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, puerto, pem):
        super().__init__(("127.0.0.1", puerto), Respuesta)
        self.contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.contexto.load_cert_chain(pem)

    def get_request(self):
        s, a = self.socket.accept()
        return self.contexto.wrap_socket(s, server_side=True), a

    def handle_error(self, request, client_address):
        pass   # (el Amiga corta la conexión al no poder comprobar el certificado: es lo que se prueba)


servidores = [ServidorTLS(44301, DASH / "tests/certs/autofirmado_a.pem"),
              ServidorTLS(44302, DASH / "tests/certs/autofirmado_b.pem")]
for s in servidores:
    threading.Thread(target=s.serve_forever, daemon=True).start()


def preparar(hd):
    shutil.copy(raiz / "build/trasfondo", Path(hd) / "trasfondo")
    shutil.copy(raiz / "build/trasfondoprefs", Path(hd) / "trasfondoprefs")
    shutil.copy(raiz / "build/barra", Path(hd) / "TrasfondoBarra")


guarda = raiz / "build/prueba_certificados"
shutil.rmtree(guarda, ignore_errors=True)
ks = os.environ.get("KS") or os.environ["DASH_KICKSTART_32"]
r = run_programs([raiz / "tests/prueba_certificados.dash"], timeout=900, workbench=True, kickstart=ks,
                 system=str(Path.home() / ".cache/dash-emu/sys32rtg32"),
                 extra_config=MACHINES["rtg"]["config"] + "bsdsocket_library = 1\n", on_disk=preparar,
                 keep=str(guarda))
print(r[0].output)
for s in servidores:
    s.shutdown()
print("capturas:", ", ".join(str(p) for p in sorted((guarda / "capturas").glob("*.png"))))
