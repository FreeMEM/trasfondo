"""El capítulo de RTG: la misma copia de Coffin después de la toma principal, arrancada con pantalla (Xvfb), que
la pone en la tarjeta gráfica a 1280x1024 y color real. Trasfondo arranca solo desde WBStartup con lo que se
guardó en la toma principal (tres tareas, sin discos). Hace falta el agente en marcha.

    python3 guion_rtg.py <carpeta de la toma>
"""
import sys
import time

import agente
import amiga
import piloto as p
from amiberry import orden
from instalar import esperar_ventana
from rodaje import Rodaje

# TrasfondoPrefs: igual que en AGA (misma fuente), medido con amiga.gadgets
PREFS = {"Ver los discos": (24, 86, 26, 11), "Guardar": (24, 180, 88, 16)}
TRASPASO = (38, 250)                  # el icono del escritorio de Coffin en RTG
ZOOM = (990, 16, 290, 232)            # el panel y algo de fondo alrededor, en 5:4


def pulsar_prefs(texto):
    v = amiga.ventana("Preferencias de Trasfondo")
    x, y, an, al = PREFS[texto]
    p.mover_a(v[2] + x + an // 2, v[3] + y + al // 2)
    p.clic()


def arrastrar(desde, hasta, dur=1.4):
    p.mover_a(*desde)
    orden("SEND_MOUSE", 0, 0, 1)
    time.sleep(0.25)
    p.mover_a(*hasta, dur=dur, botones=1)
    time.sleep(0.3)
    orden("SEND_MOUSE", 0, 0, 0)
    time.sleep(0.5)


r = Rodaje(sys.argv[1])
r.empezar()
time.sleep(1)
r.capitulo("5 - Con tarjeta gráfica", "RTG, a 1280x1024 y color real")
r.decir("Con tarjeta gráfica (RTG), Trasfondo arranca solo, con lo que se guardó.")
time.sleep(4.5)
r.decir("Con color real, el panel es translúcido: deja ver el fondo.")
r.acercar(*ZOOM, dur=20)
time.sleep(5)
agente.lanzar("C:List SYS: ALL >NIL:")             # algo de trabajo para la gráfica
r.decir("La CPU, la memoria y las tareas, igual que antes.")
time.sleep(5.5)
r.decir("Vuelvo a poner los discos con TrasfondoPrefs.")
agente.lanzar("Traspaso:Trasfondo/TrasfondoPrefs")
esperar_ventana("Preferencias de Trasfondo", 20); time.sleep(1.5)
pulsar_prefs("Ver los discos"); time.sleep(1.2)
pulsar_prefs("Guardar"); time.sleep(4)
r.decir("Los iconos siguen por encima, también aquí.")
arrastrar(TRASPASO, (1120, 110))
r.acercar(*ZOOM, dur=3.5)
time.sleep(2.5)
arrastrar((1120, 110), TRASPASO)
time.sleep(1.5)
r.decir("En AGA, o con 256 colores, el panel lleva un fondo sólido, para que se lea siempre.")
time.sleep(5.5)
r.acabar()
print("toma:", round(r.ahora(), 1), "s,", len(r.cuadros), "cuadros")
