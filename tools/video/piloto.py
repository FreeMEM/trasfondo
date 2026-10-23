"""El piloto: mueve el puntero de Coffin como una persona (con prisa al principio y frenando al llegar),
pulsa, y encuentra las cosas por su texto en la pantalla (OCR) o en las ventanas de Intuition."""
import difflib
import os
import subprocess
import tempfile
import time

from PIL import Image

import amiga
from amiberry import orden

# la imagen de SCREENSHOT: la pantalla de 640x256 empieza en (56, 38), con cada línea doble
X0, Y0, ESCALA_Y = 56, 38, 2


def a_imagen(x, y):
    return X0 + x, Y0 + y * ESCALA_Y


def a_pantalla(ix, iy):
    return ix - X0, (iy - Y0) // ESCALA_Y


def captura(ruta):
    r = orden("SCREENSHOT", ruta)
    assert r.startswith("OK"), r
    return ruta


def mover_a(x, y, dur=0.9, paso=0.03, botones=0):
    """Lleva el puntero a (x, y) de la pantalla en unos dur segundos, frenando al final. botones: los que
    siguen pulsados mientras (1, para arrastrar): cada movimiento lleva el estado de los botones."""
    x0, y0 = amiga.puntero()
    n = max(2, int(dur / paso))
    hx, hy = x0, y0                       # donde debería estar ya
    for i in range(1, n + 1):
        t = i / n
        f = 1 - (1 - t) ** 3              # rápido al salir, despacio al llegar
        nx, ny = x0 + (x - x0) * f, y0 + (y - y0) * f
        dx, dy = round(nx - hx), round((ny - hy) * ESCALA_Y)
        if dx or dy:
            orden("SEND_MOUSE", dx, dy, botones)
            hx += dx
            hy += dy / ESCALA_Y
        time.sleep(paso)
    for _ in range(5):                    # ajuste fino con lo que dice Intuition
        px, py = amiga.puntero()
        if (px, py) == (x, y):
            break
        orden("SEND_MOUSE", x - px, (y - py) * ESCALA_Y, botones)
        time.sleep(0.05)


def clic(veces=1, boton=1):
    for i in range(veces):
        orden("SEND_MOUSE", 0, 0, boton)
        time.sleep(0.06)
        orden("SEND_MOUSE", 0, 0, 0)
        time.sleep(0.08 if i + 1 < veces else 0.3)


def buscar_texto(texto, zona=None, intentos=3):
    """(x, y) en la pantalla del centro del texto que se lee en ella (OCR); None si no está."""
    for _ in range(intentos):
        with tempfile.TemporaryDirectory() as d:
            img = Image.open(captura(os.path.join(d, "c.png"))).convert("L")
            if zona:
                img = img.crop(zona)
            ox, oy = zona[:2] if zona else (0, 0)
            img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
            img.save(os.path.join(d, "g.png"))
            tsv = subprocess.run(["tesseract", os.path.join(d, "g.png"), "-", "--psm", "11", "tsv"],
                                 capture_output=True, text=True).stdout
        mejor, donde = 0.0, None             # el OCR falla letras sobre un fondo con trama: lo más parecido
        for linea in tsv.splitlines()[1:]:
            c = linea.split("\t")
            if len(c) == 12 and len(c[11].strip()) >= 3:
                r = difflib.SequenceMatcher(None, c[11].strip().lower(), texto.lower()).ratio()
                if r > mejor:
                    l, t, w, h = (int(v) for v in c[6:10])
                    mejor, donde = r, (ox + (l + w / 2) / 3, oy + (t + h / 2) / 3)
        if mejor >= 0.7:
            return a_pantalla(round(donde[0]), round(donde[1]))
        time.sleep(0.5)
    return None


def pulsar(texto, veces=1, dy=0, zona=None, dur=0.9):
    """Va al texto que se lee en la pantalla y pulsa ahí (dy: más arriba o abajo, para el icono de encima)."""
    d = buscar_texto(texto, zona)
    if not d:
        raise RuntimeError("no veo: " + texto)
    mover_a(d[0], d[1] + dy, dur)
    clic(veces)
    return d


def cerrar(titulo):
    """Pulsa el botón de cierre (arriba a la izquierda) de esa ventana."""
    v = amiga.ventana(titulo)
    if v:
        mover_a(v[2] + 6, v[3] + 5, 0.6)
        clic()
        time.sleep(0.6)


def teclas(*nombres, pausa=0.08):
    """Pulsa una combinación (las de antes se mantienen mientras se pulsa la última) y la suelta."""
    from teclas import CODIGOS
    for n in nombres:
        orden("SEND_KEY", CODIGOS[n], 1)
        time.sleep(pausa)
    for n in reversed(nombres):
        orden("SEND_KEY", CODIGOS[n], 0)
        time.sleep(pausa)
