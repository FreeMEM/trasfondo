#!/usr/bin/env python3
"""Lanza tests/prueba_commodity.dash en el emulador (AmigaOS 3.2.3 con Workbench), con build/trasfondo en DH0:.

    DASH=~/Projects/FreeMEMLang python3 tests/prueba_commodity.py [captura.png]

Pide $DASH (una copia de Dash) y $DASH_KICKSTART_32 (la ROM de 3.2.3); el sistema, ~/.cache/dash-emu/sys32.
"""

import os
import shutil
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(os.environ["DASH"], "tools"))
from emu_run import run_programs   # noqa: E402
sys.path.insert(0, str(raiz / "tools"))
from icono import icono, info, WBTOOL   # noqa: E402


def preparar(hd):
    """DH0:trasfondo, y su icono con los tooltypes que mira la prueba."""
    shutil.copy(raiz / "build/trasfondo", Path(hd) / "trasfondo")
    (Path(hd) / "trasfondo.info").write_bytes(
        info(icono(), WBTOOL, tooltypes=["CX_POPUP=NO", "CX_POPKEY=ctrl alt t"]))


capturas = [(14, sys.argv[1])] if len(sys.argv) > 1 else None
r = run_programs([raiz / "tests/prueba_commodity.dash"], timeout=180, workbench=True,
                 kickstart=os.environ["DASH_KICKSTART_32"], system=str(Path.home() / ".cache/dash-emu/sys32"),
                 screenshot=capturas,
                 on_disk=preparar)
print(r[0].output if hasattr(r[0], "output") else r[0])
