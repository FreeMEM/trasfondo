"""El montaje: de la toma (toma.json y sus capturas) al vídeo de 1920x1080, con aire de Amiga.

    python3 montar.py <carpeta de la toma> <salida.mp4>

- Rótulos entre capítulos: azul del Workbench 1.3, letra Topaz, raya naranja y una bola Boing en la portada.
- La pantalla del Amiga, a escala entera (640x256 → 1280x1024) con líneas de barrido suaves.
- Subtítulos en Topaz, quemados y además como pista; capítulos en los metadatos; un aro naranja en cada clic.
"""
import json
import math
import multiprocessing
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 25
FUENTES = os.path.expanduser("~/.cache/video-trasfondo/fuentes")
TOPAZ = os.path.join(FUENTES, "TopazPlus_a1200_v1.0.ttf")
AZUL_WB = (0, 85, 170)
NARANJA = (255, 136, 0)
BLANCO = (255, 255, 255)
FONDO = (12, 18, 30)
# la pantalla del Amiga dentro de la captura de Amiberry, y dónde va en el vídeo
RECORTE = (56, 38, 696, 550)
PX, PY, ESC_X, ESC_Y = 320, 28, 2, 4      # 1 píxel del Amiga = 2x4 del vídeo

PORTADA = 4.5
RÓTULO = 3.2
CIERRE = 6.0


def fuente(tam):
    return ImageFont.truetype(TOPAZ, tam)


def bola_boing(d):
    """La bola Boing: esfera de cuadros rojos y blancos, girada como en la demo de 1984."""
    img = Image.new("RGBA", (d, d), (0, 0, 0, 0))
    px = img.load()
    r = d / 2
    inclinacion = math.radians(-20)
    for y in range(d):
        for x in range(d):
            nx, ny = (x - r + 0.5) / r, (y - r + 0.5) / r
            if nx * nx + ny * ny > 1:
                continue
            nz = math.sqrt(1 - nx * nx - ny * ny)
            rx = nx * math.cos(inclinacion) - ny * math.sin(inclinacion)
            ry = nx * math.sin(inclinacion) + ny * math.cos(inclinacion)
            lon = math.atan2(rx, nz) + 0.35
            lat = math.asin(max(-1, min(1, ry)))
            c = (int((lon + math.pi) / (math.pi / 8)) + int((lat + math.pi / 2) / (math.pi / 8))) % 2
            luz = 0.55 + 0.45 * max(0, (-0.4 * nx - 0.5 * ny + 0.75 * nz))
            base = (230, 30, 30) if c else (245, 245, 245)
            px[x, y] = tuple(int(v * luz) for v in base) + (255,)
    return img


def rotulo(titulo, subtitulo="", portada=False, lineas=()):
    img = Image.new("RGB", (W, H), AZUL_WB)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 4):                                     # barrido, muy suave
        d.line([(0, y + 3), (W, y + 3)], fill=(0, 76, 153))
    x0 = 180
    if portada:
        bola = bola_boing(360)
        sombra = Image.new("RGBA", bola.size, (0, 0, 0, 0))
        sombra.paste((0, 40, 90, 140), mask=bola.split()[3])
        img.paste(sombra, (W - 560 + 30, 300 + 30), sombra)
        img.paste(bola, (W - 560, 300), bola)
    tam = 112 if portada else 88
    y = 360 if portada else 400
    d.text((x0, y), titulo, font=fuente(tam), fill=BLANCO)
    y += tam + 30
    d.rectangle([x0, y, x0 + 520, y + 10], fill=NARANJA)
    y += 50
    if subtitulo:
        d.text((x0, y), subtitulo, font=fuente(44), fill=(220, 230, 255))
        y += 70
    for l in lineas:
        d.text((x0, y), l, font=fuente(36), fill=(200, 215, 245))
        y += 54
    return img


def envolver(texto, f, ancho):
    palabras, lineas, l = texto.split(), [], ""
    for p in palabras:
        prueba = (l + " " + p).strip()
        if f.getlength(prueba) <= ancho:
            l = prueba
        else:
            lineas.append(l)
            l = p
    if l:
        lineas.append(l)
    return lineas


def fondo(capitulo):
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    d.text((32, 40), "Trasfondo", font=fuente(40), fill=NARANJA)
    for i, l in enumerate(envolver(capitulo, fuente(24), 270)):
        d.text((32, 110 + i * 36), l, font=fuente(24), fill=BLANCO)
    d.text((32, H - 120), "AmigaOS 3.x", font=fuente(24), fill=(150, 165, 190))
    d.text((32, H - 84), "hecho en Dash", font=fuente(24), fill=(150, 165, 190))
    d.rectangle([PX - 6, PY - 6, PX + 1280 + 5, PY + 1024 + 5], outline=(60, 70, 90), width=2)
    return img


def pantalla(fichero):
    cap = Image.open(fichero).convert("RGB").crop(RECORTE)        # 640x512: cada línea del Amiga, doble
    cap = cap.resize((640, 256), Image.NEAREST).resize((1280, 1024), Image.NEAREST)
    d = ImageDraw.Draw(cap, "RGBA")
    for y in range(3, 1024, 4):                                   # la cuarta fila de cada línea, más oscura
        d.line([(0, y), (1279, y)], fill=(0, 0, 0, 70))
    return cap


def a_video(x, y):
    return PX + x * ESC_X + ESC_X // 2, PY + y * ESC_Y + ESC_Y // 2


def componer(base, cap, t, toma):
    img = base.copy()
    img.paste(cap, (PX, PY))
    d = ImageDraw.Draw(img, "RGBA")
    for (tm, dur, _, x, y, an, al) in toma["marcas"]:
        if tm <= t <= tm + dur:
            a = min(1, (t - tm) / 0.3, (tm + dur - t) / 0.3)
            x0, y0 = a_video(x, y)
            x1, y1 = a_video(x + an, y + al)
            for k in range(3):
                d.rectangle([x0 - 4 - k, y0 - 4 - k, x1 + 4 + k, y1 + 4 + k], outline=NARANJA + (int(230 * a),))
    for (tc, x, y) in toma["clics"]:
        k = (t - tc) * FPS
        if 0 <= k < 8:
            cx, cy = a_video(x, y)
            r = 10 + k * 5
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NARANJA + (int(255 * (1 - k / 8)),), width=5)
    for (t0, t1, texto) in toma["subtitulos"]:
        if t0 <= t < t1:
            f = fuente(32)
            lineas = envolver(texto, f, 1180)[:2]
            alto = 46 * len(lineas) + 24
            y0 = PY + 1024 - alto - 24
            ancho = max(f.getlength(l) for l in lineas) + 48
            d.rounded_rectangle([960 - ancho / 2, y0, 960 + ancho / 2, y0 + alto], 10, fill=(0, 0, 0, 190))
            for i, l in enumerate(lineas):
                d.text((960 - f.getlength(l) / 2, y0 + 14 + i * 46), l, font=f, fill=BLANCO)
    return img


_toma, _fondos = None, {}


def _iniciar(toma, titulos):
    global _toma
    _toma = toma
    for titulo in titulos:
        _fondos[titulo] = fondo(titulo)


def _cuadro(trabajo):
    """Un cuadro de la toma, compuesto en un proceso aparte: (título del capítulo, hora, captura)."""
    titulo, t, fichero = trabajo
    return componer(_fondos[titulo], pantalla(fichero), t, _toma).tobytes()


def srt_tiempo(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    carpeta, salida = sys.argv[1], sys.argv[2]
    toma = json.load(open(os.path.join(carpeta, "toma.json")))
    cuadros = toma["cuadros"]
    caps = toma["capitulos"]
    cierre = toma.get("cierre", ("Trasfondo", "Libre (MIT)", ["github.com/FreeMEM/trasfondo",
                                                              "Hecho en Dash: github.com/FreeMEM/dash"]))
    # el guion: portada, y por cada capítulo su rótulo y su trozo de toma; al final, el cierre
    tramos = [("rotulo", PORTADA, rotulo("Trasfondo", "Un monitor de recursos en el fondo del Workbench",
                                         True, ["AmigaOS 3.x  -  hecho en Dash"]), "Trasfondo")]
    for i, (t0, titulo, sub) in enumerate(caps):
        t1 = caps[i + 1][0] if i + 1 < len(caps) else toma["fin"]
        tramos.append(("rotulo", RÓTULO, rotulo(titulo, sub), titulo))
        tramos.append(("toma", (t0, t1), fondo(titulo), titulo))
    tramos.append(("rotulo", CIERRE, rotulo(cierre[0], cierre[1], True, cierre[2]), cierre[0]))

    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", salida + ".crudo.mp4"], stdin=subprocess.PIPE)
    pool = multiprocessing.Pool(initializer=_iniciar, initargs=(toma, [c[1] for c in caps]))
    t_video = 0.0
    capitulos_video, srt = [], []
    j = 0
    for tipo, dur, img, nombre in tramos:
        if tipo == "rotulo":                     # cada capítulo empieza en su rótulo
            capitulos_video.append((t_video, nombre))
        if tipo == "rotulo":
            n = int(dur * FPS)
            datos = img.tobytes()
            for _ in range(n):
                ff.stdin.write(datos)
            t_video += n / FPS
            continue
        t0, t1 = dur
        for (s0, s1, texto) in toma["subtitulos"]:
            if s0 < t1 and s1 > t0:
                srt.append((t_video + max(s0, t0) - t0, t_video + min(s1, t1) - t0, texto))
        n = int((t1 - t0) * FPS)
        trabajos = []
        for k in range(n):
            t = t0 + k / FPS
            while j + 1 < len(cuadros) and cuadros[j + 1][0] <= t:
                j += 1
            trabajos.append((nombre, t, cuadros[j][1]))
        for datos in pool.imap(_cuadro, trabajos, chunksize=16):
            ff.stdin.write(datos)
        t_video += n / FPS
    ff.stdin.close()
    ff.wait()
    pool.close()

    with open(salida + ".srt", "w") as f:
        for i, (a, b, texto) in enumerate(srt, 1):
            f.write(f"{i}\n{srt_tiempo(a)} --> {srt_tiempo(b)}\n{texto}\n\n")
    with open(salida + ".ffmeta", "w") as f:
        f.write(";FFMETADATA1\ntitle=Trasfondo: instalarlo y usarlo\n")
        for i, (a, nombre) in enumerate(capitulos_video):
            b = capitulos_video[i + 1][0] if i + 1 < len(capitulos_video) else t_video
            f.write(f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(a * 1000)}\nEND={int(b * 1000)}\ntitle={nombre}\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", salida + ".crudo.mp4", "-i", salida + ".srt",
                    "-i", salida + ".ffmeta", "-map", "0:v", "-map", "1:s", "-map_metadata", "2",
                    "-map_chapters", "2", "-c:v", "copy", "-c:s", "mov_text", "-metadata:s:s:0", "language=spa",
                    "-movflags", "+faststart", salida], check=True)
    os.remove(salida + ".crudo.mp4")
    print(salida, f"{t_video:.1f} s")


if __name__ == "__main__":
    main()
