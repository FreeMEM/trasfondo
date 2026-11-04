#!/usr/bin/env python3
"""Lanza tests/prueba_actualizar.dash en el emulador (AmigaOS 3.2.3 con RTG y la red del PC), con dos instalaciones:
DH0:T1 (el fondo y TrasfondoPrefs de build/release, sin piezas) y DH0:T2 (un fondo que dice ser la 2.0.9, con piezas
viejas de 5 bytes). Necesita la release v2.1 en GitHub (de prueba, sin marcar como última).

    DASH=~/Projects/FreeMEMLang PYTHONPATH=$DASH KS=kick323.rom python3 tests/prueba_actualizar.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
DASH = Path(os.environ["DASH"])
sys.path.insert(0, str(DASH / "tools"))
from emu_run import run_programs, MACHINES   # noqa: E402

rel = raiz / "build/release"
vieja = raiz / "build/trasfondo-209"
fuente = raiz / "src/_trasfondo_209.dash"
fuente.write_text((raiz / "src/trasfondo.dash").read_text().replace('@version "Trasfondo 2.1"', '@version "Trasfondo 2.0.9"'))
subprocess.run([str(DASH / "dash"), str(fuente), "-o", str(vieja)], cwd=raiz / "src", check=True,
               env=dict(os.environ, PYTHONPATH=str(DASH)))
fuente.unlink()


def preparar(hd):
    t1 = Path(hd) / "T1"
    t1.mkdir()
    shutil.copy(rel / "trasfondo", t1 / "trasfondo")
    shutil.copy(rel / "TrasfondoPrefs", t1 / "TrasfondoPrefs")
    t2 = Path(hd) / "T2"
    t2.mkdir()
    shutil.copy(vieja, t2 / "trasfondo")
    shutil.copy(rel / "TrasfondoPrefs", t2 / "TrasfondoPrefs")
    for p in ("TrasfondoBarra", "TrasfondoPanel", "TrasfondoAviso", "TrasfondoRapido", "TrasfondoDock", "TrasfondoVentanas"):
        (t2 / p).write_bytes(b"viejo")


ks = os.environ.get("KS") or os.environ["DASH_KICKSTART_32"]
r = run_programs([raiz / "tests/prueba_actualizar.dash"], timeout=900, workbench=True, kickstart=ks,
                 system=str(Path.home() / ".cache/dash-emu/sys32rtg32"),
                 extra_config=MACHINES["rtg"]["config"] + "bsdsocket_library = 1\n", on_disk=preparar,
                 keep=str(raiz / "build/prueba_actualizar"))
print(r[0].output)
# la herramienta del icono de arranque de la barra que hizo el actualizador
icono = raiz / "build/prueba_actualizar/T1/Arranque/TrasfondoBarra.info"
if icono.exists():
    d = icono.read_bytes()
    i = d.find(b"TrasfondoBarra\0")
    j = d.rfind(b"\0\0", 0, i)
    print("icono barra:", d[j + 2:i + 14], "tooltypes:", b"DONOTWAIT" in d)
else:
    print("icono barra: no está")
