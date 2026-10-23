"""La instalación en Coffin, paso a paso, con el piloto. Devuelve cuando el Installer ha acabado."""
import time

import amiga
import piloto as p

TRASPASO = (118, 70)          # los iconos del escritorio de Coffin (no se mueven)
SYSTEM = (116, 105)


def icono_en(titulo, x, y, ancho=34, alto=18):
    """El centro de un icono puesto en (x, y) dentro de la ventana de ese título."""
    v = amiga.ventana(titulo)
    bl, bt = amiga.bordes(v[0])
    return v[2] + bl + x + ancho // 2, v[3] + bt + y + alto // 2


def boton(cual=0):
    """Pulsa un botón del Installer: 0 el de arriba a la izquierda (Seguir, Sí), 1 el de su derecha (No,
    Abortar), 2 el único y centrado de las páginas de mensaje. No dicen su texto a Intuition, pero van
    siempre ahí (medido: ventana de 496x210)."""
    v = amiga.ventana("Instalar")
    dx, dy = ((8, 172), (250, 172), (129, 189))[cual]
    p.mover_a(v[2] + dx + 119, v[3] + dy + 8)
    p.clic()


def esperar_ventana(titulo, tope=15):
    t = time.time()
    while time.time() - t < tope:
        if amiga.ventana(titulo):
            return True
        time.sleep(0.3)
    return False


def instalar(arrancar=True):
    p.mover_a(*TRASPASO); p.clic(2)
    esperar_ventana("Traspaso"); time.sleep(1)
    p.mover_a(*icono_en("Traspaso", 10, 6, 40, 20)); p.clic(2)
    esperar_ventana("Trasfondo"); time.sleep(1)
    p.mover_a(*icono_en("Trasfondo", 10, 6)); p.clic(2)
    esperar_ventana("Instalar"); time.sleep(2)
    boton(0); time.sleep(1.5)                    # modo de instalación: Seguir
    boton(0); time.sleep(1.5)                    # opciones: Seguir
    boton(0); time.sleep(3)                      # ¿arranca con el Workbench? Sí
    boton(0 if arrancar else 1); time.sleep(3)   # ¿lo pongo en marcha?
    boton(0); time.sleep(1.5)                    # el mensaje final: Seguir
    boton(0); time.sleep(1.5)                    # ¡Instalación completa!: Seguir
