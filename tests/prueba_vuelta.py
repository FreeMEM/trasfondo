#!/usr/bin/env python3
"""Lanza tests/prueba_vuelta.dash en el emulador (AmigaOS 3.2.3 con Workbench), con build/trasfondo y
build/trasfondoprefs en DH0:, y guarda una captura (FICHERO.png, a los SEGUNDOS).

    DASH=~/Projects/FreeMEMLang PYTHONPATH=$DASH DASH_KICKSTART_32=kick323.rom python3 tests/prueba_vuelta.py FICHERO.png SEGUNDOS
"""

import os
import re
import shutil
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(os.environ["DASH"], "tools"))
from emu_run import run_programs   # noqa: E402

version = re.search(r'@version "TrasfondoPrefs ([^"]+)"', (raiz / "src/trasfondoprefs.dash").read_text()).group(1)


def preparar(hd):
    for p in ("trasfondo", "trasfondoprefs"):
        shutil.copy(raiz / "build" / p, Path(hd) / p)
    (Path(hd) / "version_prueba").write_text(version + "\n")


r = run_programs([raiz / "tests/prueba_vuelta.dash"], timeout=180, workbench=True,
                 kickstart=os.environ["DASH_KICKSTART_32"], system=str(Path.home() / ".cache/dash-emu/sys32"),
                 on_disk=preparar, screenshot=(int(sys.argv[2]), sys.argv[1]) if len(sys.argv) > 2 else None)
print(r[0].output)
