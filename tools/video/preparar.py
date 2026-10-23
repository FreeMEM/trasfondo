"""Deja Coffin listo para la toma, sin tocar el Coffin del usuario: una copia nueva del disco (reflink), Traspaso
con el paquete, Amiberry sin ventana, y el agente en marcha (su icono se borra antes de grabar).

    python3 preparar.py
"""
import glob
import os
import shutil
import subprocess
import time

import amiga
import piloto as p
from amiberry import orden
from instalar import TRASPASO, icono_en, esperar_ventana

V = os.path.expanduser("~/.cache/video-trasfondo")
ORIGINAL = os.path.expanduser("~/Amiberry/HardDrives/coffin_r65_32GB.img")
PAQUETE = os.path.expanduser("~/Projects/trasfondo/build/paquete")
TRASP = os.path.join(V, "traspaso")


def cerrar_amiberry():
    """Cierra el Amiberry de la toma anterior (por su PID, no por su nombre) y espera a que se vaya del todo."""
    fpid = os.path.join(V, "amiberry.pid")
    if os.path.exists(fpid):
        pid = int(open(fpid).read())
        for ruta in glob.glob(os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "amiberry*.sock")):
            try:
                orden("QUIT", ruta=ruta)
            except OSError:
                pass
        for _ in range(60):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.5)
        else:
            os.kill(pid, 9)
        os.remove(fpid)
    for ruta in glob.glob(os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"), "amiberry*.sock")):
        os.remove(ruta)                          # sin dueño ya: que la nueva use la de siempre


def main():
    cerrar_amiberry()
    subprocess.run(["cp", "--reflink=always", ORIGINAL, os.path.join(V, "coffin-video.img")], check=True)
    shutil.rmtree(TRASP, ignore_errors=True)
    os.makedirs(TRASP)
    shutil.copytree(os.path.join(PAQUETE, "Trasfondo"), os.path.join(TRASP, "Trasfondo"))
    shutil.copy(os.path.join(PAQUETE, "Trasfondo.info"), TRASP)
    shutil.copy(os.path.expanduser("~/Projects/trasfondo/build/trasfondo-0.2.lha"), TRASP)
    for f in ("agente", "agente.info"):
        shutil.copy(os.path.join(V, "agente", f), TRASP)
    env = dict(os.environ, SDL_VIDEODRIVER="offscreen", SDL_AUDIODRIVER="dummy")
    pr = subprocess.Popen(["amiberry", "-f", os.path.join(V, "video.uae"), "-s", "use_gui=no"], env=env,
                     stdout=open(os.path.join(V, "amiberry.log"), "w"), stderr=subprocess.STDOUT,
                     start_new_session=True)
    open(os.path.join(V, "amiberry.pid"), "w").write(str(pr.pid))
    t = time.time()
    while time.time() - t < 120:                 # hasta que el Workbench esté y quieto
        try:
            if "Workbench" in amiga.tareas() and "AutoUpdateWB" in amiga.tareas():
                break
        except (OSError, AssertionError, RuntimeError):
            amiga._ib = None
        time.sleep(2)
    time.sleep(15)
    p.mover_a(*TRASPASO); p.clic(2)
    esperar_ventana("Traspaso"); time.sleep(1.5)
    p.mover_a(*icono_en("Traspaso", 100, 6)); p.clic(2)
    time.sleep(2)
    p.cerrar("Traspaso")
    for f in ("agente", "agente.info"):
        os.remove(os.path.join(TRASP, f))
    p.mover_a(300, 150)
    print("agente:", "agente" in amiga.tareas())


if __name__ == "__main__":
    main()
