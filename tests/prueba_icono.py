#!/usr/bin/env python3
"""act_icono_archivos en el emulador (tests/prueba_icono.dash): quien actualizó a la 2.9 con el botón tiene
TrasfondoArchivos sin .info y el Workbench no lo enseña. DH0:T3 tiene el explorador y TrasfondoBarra.info: sale
TrasfondoArchivos.info, el de la barra sin sitio fijo. DH0:T4 no tiene explorador y DH0:T5 no tiene otro icono: no se
crea nada. Necesita build/paquete (DASH=... python3 tools/paquete.py X.Y).

    DASH=~/Projects/FreeMEMLang flock /run/user/1000/dash-emu-red.lock python3 tests/prueba_icono.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
DASH = Path(os.environ["DASH"])
sys.path.insert(0, str(DASH / "tools"))
from emu_run import run_programs   # noqa: E402

ico = raiz / "build/paquete/Trasfondo/TrasfondoBarra.info"
tmp = Path(tempfile.mkdtemp())
fuente = raiz / "src/_prueba_icono.dash"
shutil.copy(raiz / "tests/prueba_icono.dash", fuente)
try:
    subprocess.run([str(DASH / "dash"), str(fuente), "-o", str(tmp / "prueba_icono")], cwd=raiz / "src", check=True,
                   env=dict(os.environ, PYTHONPATH=str(DASH)))
finally:
    fuente.unlink()


def preparar(hd):
    for t in ("T3", "T4", "T5"):
        (Path(hd) / t).mkdir()
    (Path(hd) / "T3/TrasfondoArchivos").write_bytes(b"x")
    shutil.copy(ico, Path(hd) / "T3/TrasfondoBarra.info")
    shutil.copy(ico, Path(hd) / "T4/TrasfondoBarra.info")
    (Path(hd) / "T5/TrasfondoArchivos").write_bytes(b"x")


r = run_programs([tmp / "prueba_icono"], timeout=120, on_disk=preparar, keep=str(tmp / "hd"))
salida = r[0].output
print(salida)
a = (tmp / "hd/T3/TrasfondoArchivos.info").read_bytes()
b = ico.read_bytes()
distintos = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
bien = (len(a) == len(b) and set(distintos) <= {58, 59, 60, 61, 62, 63, 64, 65}
        and "x -2147483648 y -2147483648" in salida and "sin explorador: false" in salida
        and "sin otros iconos: false" in salida)
shutil.rmtree(tmp)
print("TODO BIEN" if bien else "FALLO")
sys.exit(0 if bien else 1)
