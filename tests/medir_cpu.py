#!/usr/bin/env python3
"""Lanza tests/medir_cpu.dash en el emulador, con build/trasfondo en DH0:.

    DASH=~/Projects/FreeMEMLang PYTHONPATH=$DASH DASH_KICKSTART_32=kick323.rom python3 tests/medir_cpu.py [planar|rtg] [argumentos]

planar: A1200 con su 68020 (pantalla AGA). rtg: 68030 a velocidad real, sin JIT, con tarjeta uaegfx (pantalla de 16 bits).
Los argumentos van a trasfondo como tooltypes (INTERVAL=1 BACKGROUND=SOLID...).
"""

import os
import shutil
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(os.environ["DASH"], "tools"))
from emu_run import run_programs   # noqa: E402

maquina = sys.argv[1] if len(sys.argv) > 1 else "planar"
argumentos = " ".join(sys.argv[2:])


def preparar(hd):
    shutil.copy(raiz / "build/trasfondo", Path(hd) / "trasfondo")
    (Path(hd) / "argumentos.txt").write_text(argumentos + "\n")


config, sistema = "", "sys32"
if maquina == "rtg":
    config, sistema = "cpu = 68030\nuae_cpu_speed = real\nzorro_iii_memory = 65536\ngraphics_card = uaegfx\n", "sys32rtg"
r = run_programs([raiz / "tests/medir_cpu.dash"], timeout=240, workbench=True, extra_config=config,
                 kickstart=os.environ["DASH_KICKSTART_32"], system=str(Path.home() / ".cache/dash-emu" / sistema),
                 on_disk=preparar)
print(r[0].output)
