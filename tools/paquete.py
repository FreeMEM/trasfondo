#!/usr/bin/env python3
"""El paquete de Trasfondo para Aminet y GitHub: el cajón Trasfondo con sus iconos y el .lha.

    python3 tools/paquete.py 0.2        →  build/paquete/Trasfondo/...  y  build/trasfondo-0.2.lha

Necesita build/trasfondo y build/trasfondoprefs compilados, y el lha de 68k (/opt/amiga/bin/lha) para que
el archivo guarde bien los atributos.
"""

import shutil
import subprocess
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz / "tools"))
from icono import icono, icono_prefs, info, WBTOOL, TOOLTYPES   # noqa: E402
from iconos_wb import cajon, documento, instalador, WBDRAWER, WBPROJECT   # noqa: E402


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "0.0"
    dest = raiz / "build/paquete"
    shutil.rmtree(dest, ignore_errors=True)
    caj = dest / "Trasfondo"
    caj.mkdir(parents=True)
    (dest / "Trasfondo.info").write_bytes(info(cajon(), WBDRAWER))
    shutil.copy(raiz / "build/trasfondo", caj / "trasfondo")
    (caj / "trasfondo.info").write_bytes(info(icono(), WBTOOL, tooltypes=TOOLTYPES))
    shutil.copy(raiz / "build/trasfondoprefs", caj / "TrasfondoPrefs")
    (caj / "TrasfondoPrefs.info").write_bytes(info(icono_prefs(), WBTOOL))
    shutil.copy(raiz / "paquete/Instalar", caj / "Instalar")
    (caj / "Instalar.info").write_bytes(
        info(instalador(), WBPROJECT, herramienta="Installer",
             tooltypes=["APPNAME=Trasfondo", "MINUSER=AVERAGE", "DEFUSER=AVERAGE"]))
    shutil.copy(raiz / "README.md", caj / "LEEME")
    (caj / "LEEME.info").write_bytes(info(documento(), WBPROJECT, herramienta="SYS:Utilities/MultiView"))
    shutil.copy(raiz / "LICENSE", caj / "LICENSE")
    lha = raiz / f"build/trasfondo-{version}.lha"
    lha.unlink(missing_ok=True)
    subprocess.run(["/opt/amiga/bin/lha", "ao5q", str(lha), "Trasfondo", "Trasfondo.info"]
                   + [f"Trasfondo/{p.name}" for p in sorted(caj.iterdir())], cwd=dest, check=True)
    print(lha)


if __name__ == "__main__":
    main()
