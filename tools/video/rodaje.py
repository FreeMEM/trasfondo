"""La toma: un hilo saca capturas de Amiberry a 25 por segundo (con su hora) mientras el guion maneja el
Amiga; el guion va marcando subtítulos, capítulos y clics con la hora de la toma. El montaje (montar.py)
hace el vídeo con eso: la hora de la toma manda, así los subtítulos cuadran aunque algo vaya lento."""
import json
import os
import threading
import time

import amiga
import piloto
from amiberry import orden

FPS = 25


class Rodaje:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        os.makedirs(carpeta, exist_ok=True)
        self.cuadros = []          # (t, fichero)
        self.subtitulos = []       # [t0, t1, texto]
        self.capitulos = []        # (t, título, subtítulo)
        self.clics = []            # (t, x, y)
        self.marcas = []           # (t, nombre, x, y, ancho, alto): recuadros que se resaltan en el montaje
        self.zooms = []            # (t0, t1, x, y, ancho, alto): acercamientos
        self._parar = False
        self._t0 = None
        self._clic_original = piloto.clic

    def ahora(self):
        return time.time() - self._t0

    def _capturar(self):
        n = 0
        while not self._parar:
            t = self.ahora()
            f = os.path.join(self.carpeta, f"f{n:06d}.png")
            try:
                orden("SCREENSHOT", f)
                self.cuadros.append((t, f))
                n += 1
            except OSError:
                pass
            espera = (n / FPS) - self.ahora()
            if espera > 0:
                time.sleep(espera)

    def empezar(self):
        s = amiga.pantalla()
        self.pantalla = (amiga.rd(s + 12, 2), amiga.rd(s + 14, 2))    # 640x256 nativa o la de la tarjeta (RTG)
        self._t0 = time.time()
        rodaje = self

        def clic(veces=1, boton=1):
            x, y = amiga.puntero()
            rodaje.clics.append((rodaje.ahora(), x, y))
            rodaje._clic_original(veces, boton)
        piloto.clic = clic
        self._hilo = threading.Thread(target=self._capturar, daemon=True)
        self._hilo.start()

    def decir(self, texto):
        self.callar()
        self.subtitulos.append([self.ahora(), None, texto])

    def callar(self):
        if self.subtitulos and self.subtitulos[-1][1] is None:
            self.subtitulos[-1][1] = self.ahora()

    def capitulo(self, titulo, subtitulo=""):
        self.callar()
        self.capitulos.append((self.ahora(), titulo, subtitulo))

    def marcar(self, nombre, x, y, ancho, alto, dur=3.0):
        """Un recuadro naranja sobre esa zona de la pantalla del Amiga, durante dur segundos."""
        self.marcas.append((self.ahora(), dur, nombre, x, y, ancho, alto))

    def acercar(self, x, y, ancho, alto, dur):
        """Un acercamiento a esa zona de la pantalla del Amiga (mejor en proporción 5:4) durante dur segundos."""
        self.zooms.append((self.ahora(), self.ahora() + dur, x, y, ancho, alto))

    def esperar(self, s):
        time.sleep(s)

    def acabar(self):
        self.callar()
        self._parar = True
        self._hilo.join()
        piloto.clic = self._clic_original
        with open(os.path.join(self.carpeta, "toma.json"), "w") as f:
            json.dump({"fin": self.ahora(), "pantalla": self.pantalla, "cuadros": self.cuadros, "subtitulos": self.subtitulos,
                       "capitulos": self.capitulos, "clics": self.clics, "marcas": self.marcas,
                       "zooms": self.zooms}, f,
                      ensure_ascii=False, indent=1)
