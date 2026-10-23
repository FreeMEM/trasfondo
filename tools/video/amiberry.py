"""Cliente del socket de control de Amiberry: órdenes de una línea (ORDEN\targ\targ...) y su respuesta."""
import os
import socket

RUTA = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "amiberry.sock")


def orden(*partes, ruta=RUTA):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect(ruta)
    s.sendall(("\t".join(str(p) for p in partes) + "\n").encode())
    r = b""
    while b"\n" not in r:
        c = s.recv(65536)
        if not c:
            break
        r += c
    s.close()
    return r.decode(errors="replace").strip()
