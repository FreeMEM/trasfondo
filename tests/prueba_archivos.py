#!/usr/bin/env python3
"""Lanza tests/prueba_archivos.dash en el emulador (AmigaOS 3.2.3 con Workbench, RTG y MUI), con build/archivos en
DH0:Archivos. Usa la red del PC (bsdsocket de FS-UAE): con flock /run/user/1000/dash-emu-red.lock si hay otras
pruebas con red.

    DASH=~/Projects/FreeMEMLang python3 tests/prueba_archivos.py [SEG:captura.png...]

Pide $DASH (una copia de Dash) y $DASH_KICKSTART_32 (la ROM de 3.2.3); el sistema, ~/.cache/dash-emu/sys32rtg32.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
dash = Path(os.environ["DASH"])
sys.path.insert(0, str(dash / "tools"))
from emu_run import run_programs, MACHINES   # noqa: E402

(raiz / "build").mkdir(exist_ok=True)
subprocess.run([str(dash / "dash"), "src/archivos.dash", "-o", "build/archivos", "-q"], cwd=raiz, check=True,
               env=dict(os.environ, PYTHONPATH=str(dash)))


def preparar(hd):
    shutil.copy(raiz / "build/archivos", Path(hd) / "Archivos")


capturas = [(float(a.split(":")[0]), a.split(":")[1]) for a in sys.argv[1:]] or None
r = run_programs([raiz / "tests/prueba_archivos.dash"], timeout=600, workbench=True,
                 kickstart=os.environ["DASH_KICKSTART_32"],
                 system=str(Path.home() / ".cache/dash-emu/sys32rtg32"),
                 extra_config=MACHINES["rtg"]["config"] + "bsdsocket_library = 1\n",
                 screenshot=capturas, on_disk=preparar)
print(r[0].output if hasattr(r[0], "output") else r[0])
