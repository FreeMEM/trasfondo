"""El guion del vídeo de Trasfondo: instalarlo y usarlo, en Coffin R65 (Amiberry). Se lanza con Coffin ya
arrancado y el agente en marcha (preparar.py).

    python3 guion.py <carpeta de la toma>
"""
import sys
import time

import agente
import amiga
import piloto as p
from instalar import TRASPASO, icono_en, esperar_ventana, boton
from rodaje import Rodaje

RAM_DISK = (27, 56)
CTRL, LALT, RCOMMAND = 0x0008, 0x0010, 0x0080
TECLA_T, TECLA_X, RETURN = 0x14, 0x32, 0x44

r = Rodaje(sys.argv[1])


# TrasfondoPrefs: dónde está cada gadget dentro de su ventana (medido con amiga.gadgets en Coffin; leerlos
# en plena toma cuesta segundos)
PREFS = {"Ver la gráfica de la CPU": (24, 38, 26, 11), "Ver la memoria libre": (24, 54, 26, 11),
         "Ver las tareas": (24, 70, 26, 11), "Ver los discos": (24, 86, 26, 11),
         "Ver la red y la WiFi": (24, 102, 26, 11), "Cuántas tareas": (134, 122, 48, 11),
         "Tecla rápida": (134, 140, 168, 11), "Arrancar oculto": (24, 158, 26, 11),
         "Guardar": (24, 180, 88, 16), "Usar": (122, 180, 88, 16), "Cancelar": (220, 180, 88, 16)}


def pulsar_gadget(ventana, texto, dur=0.8):
    v = amiga.ventana(ventana)
    x, y, an, al = PREFS[texto]
    p.mover_a(v[2] + x + (an // 2 if an < 40 else 12), v[3] + y + al // 2, dur)
    p.clic()


def boton_prefs(i):
    pulsar_gadget("Preferencias de Trasfondo", ("Guardar", "Usar", "Cancelar")[i])


def arrastrar(desde, hasta, dur=1.4):
    p.mover_a(*desde)
    from amiberry import orden
    orden("SEND_MOUSE", 0, 0, 1)
    time.sleep(0.25)
    p.mover_a(*hasta, dur=dur, botones=1)
    time.sleep(0.3)
    orden("SEND_MOUSE", 0, 0, 0)
    time.sleep(0.5)


def abrir_cajon():
    p.mover_a(*TRASPASO); p.clic(2)
    esperar_ventana("Traspaso"); time.sleep(1.2)
    p.mover_a(*icono_en("Traspaso", 10, 6, 40, 20)); p.clic(2)
    esperar_ventana("Trasfondo"); time.sleep(1.2)


r.empezar()
time.sleep(1.0)

# --- 1. Instalar ---
r.capitulo("1 - Instalar", "Del .lha al fondo del Workbench")
r.decir("Descomprime trasfondo-0.2.lha donde quieras. Aquí está en Traspaso:.")
time.sleep(1.5)
p.mover_a(*TRASPASO, dur=1.2); p.clic(2)
esperar_ventana("Traspaso"); time.sleep(1.5)
r.decir("Sale el cajón Trasfondo.")
p.mover_a(*icono_en("Traspaso", 10, 6, 40, 20)); time.sleep(0.6); p.clic(2)
esperar_ventana("Trasfondo"); time.sleep(0.8)
r.decir("Dentro: el instalador, el programa, sus preferencias y el LEEME.")
v = amiga.ventana("Trasfondo")
bl, bt = amiga.bordes(v[0])
r.marcar("iconos", v[2] + bl + 6, v[3] + bt + 2, 290, 34, 3.5)
time.sleep(4)
r.decir("Doble clic en Instalar: el Installer de siempre.")
p.mover_a(*icono_en("Trasfondo", 10, 6)); time.sleep(0.5); p.clic(2)
esperar_ventana("Instalar"); time.sleep(3)
r.decir("Modo de instalación y opciones: lo de siempre, Seguir.")
boton(0); time.sleep(2.2)
boton(0); time.sleep(2.5)
r.decir("¿Que arranque solo con el Workbench? Sí: se copia a SYS:WBStartup.")
time.sleep(3.5)
boton(0); time.sleep(2.5)
r.decir("Sus preferencias van a SYS:Prefs. Y lo pone en marcha ya.")
time.sleep(3)
boton(0); time.sleep(3)
r.decir("Listo.")
boton(2); time.sleep(1.8)
boton(2); time.sleep(1.5)
r.callar()
p.cerrar("Trasfondo"); p.cerrar("Traspaso")
time.sleep(2)

# --- 2. Qué enseña ---
r.capitulo("2 - Qué enseña", "Pintado en el fondo, detrás de los iconos")
agente.lanzar("C:List SYS: ALL >NIL:")              # algo de trabajo, para que la gráfica tenga historia
r.decir("El panel va pintado en el propio fondo del Workbench.")
time.sleep(3.5)
r.decir("Arriba, la CPU en uso y su historia del último minuto.")
r.marcar("cpu", 378, 26, 260, 52, 4)
time.sleep(4.5)
r.decir("La memoria Chip y Fast libre.")
r.marcar("memoria", 378, 82, 260, 20, 3)
time.sleep(3.5)
r.decir("Las tareas que más CPU toman, medidas de verdad, tarea a tarea.")
r.marcar("tareas", 378, 105, 260, 56, 4)
time.sleep(4.5)
r.decir("Y los discos: cuánto está lleno cada uno. Con Roadshow, también la red y la WiFi.")
r.marcar("discos", 378, 164, 260, 50, 4.5)
time.sleep(5)
r.decir("No tapa nada: los iconos siguen por encima.")
arrastrar(RAM_DISK, (470, 120))
time.sleep(2.5)
arrastrar((470, 120), RAM_DISK)
time.sleep(1.5)
r.decir("Y se actualiza cada segundo, gaste lo que gaste el Amiga.")
for _ in range(2):                                   # algo de trabajo para la gráfica
    p.mover_a(116, 105); p.clic(2); esperar_ventana("System"); time.sleep(1.5); p.cerrar("System")
time.sleep(3)
r.callar()

# --- 3. Elegir qué se ve ---
r.capitulo("3 - Elegir qué se ve", "TrasfondoPrefs")
r.decir("TrasfondoPrefs, en SYS:Prefs y en el cajón, dice qué se ve.")
abrir_cajon()
p.mover_a(*icono_en("Trasfondo", 170, 6)); time.sleep(0.4); p.clic(2)
esperar_ventana("Preferencias de Trasfondo"); time.sleep(2.5)
r.decir("Quito las tareas y los discos...")
pulsar_gadget("Preferencias de Trasfondo", "Ver las tareas"); time.sleep(0.8)
pulsar_gadget("Preferencias de Trasfondo", "Ver los discos"); time.sleep(1.2)
r.decir("... y Usar: el panel cambia al momento, sin reiniciar nada.")
boton_prefs(1); time.sleep(4.5)
r.decir("Vuelvo a abrirlo: las tareas otra vez, pero solo tres.")
p.mover_a(*icono_en("Trasfondo", 170, 6)); time.sleep(0.4); p.clic(2)
esperar_ventana("Preferencias de Trasfondo"); time.sleep(2)
pulsar_gadget("Preferencias de Trasfondo", "Ver las tareas"); time.sleep(0.8)
pulsar_gadget("Preferencias de Trasfondo", "Cuántas tareas"); time.sleep(0.5)
agente.tecla(TECLA_X, RCOMMAND)                      # Amiga derecha + X: borra el campo
agente.escribir("3"); agente.tecla(RETURN); time.sleep(0.4)
p.mover_a(150, 230, 0.6); time.sleep(0.8)
r.decir("Y una tecla rápida para ocultarlo y mostrarlo.")
pulsar_gadget("Preferencias de Trasfondo", "Tecla rápida"); time.sleep(0.5)
agente.escribir("ctrl alt t"); agente.tecla(RETURN); time.sleep(0.4)
p.mover_a(150, 230, 0.6); time.sleep(1.2)
r.decir("Guardar: así se queda para siempre.")
boton_prefs(0); time.sleep(4)
p.cerrar("Trasfondo"); p.cerrar("Traspaso")
r.decir("Ctrl Alt T: se oculta... y vuelve, con la historia completa.")
time.sleep(1.5)
agente.tecla(TECLA_T, CTRL | LALT); time.sleep(2.5)
agente.tecla(TECLA_T, CTRL | LALT); time.sleep(3)
r.callar()

# --- 4. Desde Exchange ---
r.capitulo("4 - Desde Exchange", "Es una commodity")
r.decir("Es una commodity: sale en Exchange, con las demás.")
agente.lanzar("SYS:Tools/Commodities/Exchange")
esperar_ventana("Exchange"); time.sleep(2)
v = amiga.ventana("Exchange")
arrastrar((v[2] + v[4] - 4, v[3] + v[5] - 4), (v[2] + v[4] - 4, 248), dur=1.0)   # más alta: se ve la lista entera
time.sleep(1.5)
p.pulsar("Trasfondo"); time.sleep(2)
v = amiga.ventana("Exchange")


def boton_ex(dx, dy):
    """Los botones de Exchange van dentro de un solo gadget de ReAction: por su sitio en la ventana."""
    p.mover_a(v[2] + dx, v[3] + dy)
    p.clic()


r.decir("Ocultar Interface quita el panel; sigue midiendo.")
boton_ex(240, 95); time.sleep(3.5)
r.decir("Ver Interface lo trae de vuelta.")
boton_ex(371, 95); time.sleep(4)
r.decir("Y Borrar lo cierra: el fondo queda como estaba. Otro doble clic en su icono, también.")
time.sleep(1.5)
boton_ex(371, 116); time.sleep(4.5)
p.cerrar("Exchange")
time.sleep(2)
r.acabar()
print("toma:", round(r.ahora(), 1), "s,", len(r.cuadros), "cuadros")
