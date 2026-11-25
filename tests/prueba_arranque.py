#!/usr/bin/env python3
"""Lanza tests/prueba_arranque.dash en el emulador (AmigaOS 3.2.3 con Workbench en RTG: la ventana de TrasfondoPrefs no cabe en 640x256), con el cajón Trasfondo del .lha de
build/ (el de tools/paquete.py) en DH0:T2, copiado tal cual, y su Arranque/Trasfondo.info en DH0:Malo.info.

    DASH=~/Projects/FreeMEMLang PYTHONPATH=$DASH DASH_KICKSTART_32=kick323.rom python3 tests/prueba_arranque.py [captura.png segundos]
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(os.environ["DASH"], "tools"))
from emu_run import MACHINES, run_programs   # noqa: E402

lha = sorted((raiz / "build").glob("trasfondo-*.lha"))[-1]
fuera = Path(tempfile.mkdtemp(prefix="arranque_"))
subprocess.run(["lha", "xqw=" + str(fuera), str(lha)], check=True)


def preparar(hd):
    hd = Path(hd)
    shutil.copytree(fuera / "Trasfondo", hd / "T2")
    if (raiz / "build/TrasfondoPrefs").exists():          # la de este árbol, si se compiló, en vez de la del .lha
        shutil.copy(raiz / "build/TrasfondoPrefs", hd / "T2/TrasfondoPrefs")
    # (en SYS:WBStartup lo pone la prueba ya arrancada: al arrancar, el Workbench se queda en su aviso "Unable to
    # open your tool" y todo lo que le habla espera)
    shutil.copy(fuera / "Trasfondo/Arranque/Trasfondo.info", hd / "Malo.info")


r = run_programs([raiz / "tests/prueba_arranque.dash"], timeout=240, workbench=True,
                 kickstart=os.environ["DASH_KICKSTART_32"], system=str(Path.home() / ".cache/dash-emu/sys32rtg32"),
                 extra_config=MACHINES["rtg"]["config"],
                 on_disk=preparar, screenshot=[(int(s), sys.argv[1].replace(".png", f"-{s}.png")) for s in sys.argv[2:]] if len(sys.argv) > 2 else None)
shutil.rmtree(fuera)
print(r[0].output)
