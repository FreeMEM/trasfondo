#!/usr/bin/env python3
"""Lanza tests/prueba_ventanas.dash en el emulador (AmigaOS 3.2.3 con Workbench), con build/ventanas en DH0:.

    DASH=~/Projects/FreeMEMLang python3 tests/prueba_ventanas.py [captura.png]

Pide $DASH (una copia de Dash) y $DASH_KICKSTART_32 (la ROM de 3.2.3); el sistema, ~/.cache/dash-emu/sys32.
Compila antes src/ventanas.dash con ese Dash.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
dash = Path(os.environ["DASH"])
sys.path.insert(0, str(dash / "tools"))
from emu_run import run_programs   # noqa: E402

(raiz / "build").mkdir(exist_ok=True)
subprocess.run([str(dash / "dash"), "src/ventanas.dash", "-o", "build/ventanas", "-q"], cwd=raiz, check=True,
               env=dict(os.environ, PYTHONPATH=str(dash)))


def preparar(hd):
    shutil.copy(raiz / "build/ventanas", Path(hd) / "ventanas")


capturas = [(40, sys.argv[1])] if len(sys.argv) > 1 else None
r = run_programs([raiz / "tests/prueba_ventanas.dash"], timeout=900, workbench=True,
                 kickstart=os.environ["DASH_KICKSTART_32"], system=str(Path.home() / ".cache/dash-emu/sys32"),
                 screenshot=capturas, on_disk=preparar)
print(r[0].output if hasattr(r[0], "output") else r[0])
