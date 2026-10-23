#!/usr/bin/env python3
"""El paquete de Trasfondo para Aminet y GitHub: el cajón Trasfondo con sus iconos y el .lha.

    python3 tools/paquete.py 0.3        →  build/paquete/Trasfondo/...  y  build/trasfondo-0.3.lha

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


def situar(icono, x, y):
    """El icono en (x, y) de su cajón (do_CurrentX/Y; sin esto, el Workbench lo coloca donde quiere)."""
    b = bytearray(icono)
    b[58:62] = x.to_bytes(4, "big")
    b[62:66] = y.to_bytes(4, "big")
    return bytes(b)


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "0.0"
    dest = raiz / "build/paquete"
    shutil.rmtree(dest, ignore_errors=True)
    caj = dest / "Trasfondo"
    caj.mkdir(parents=True)
    (dest / "Trasfondo.info").write_bytes(situar(info(cajon(), WBDRAWER), 10, 6))
    shutil.copy(raiz / "build/trasfondo", caj / "trasfondo")
    (caj / "trasfondo.info").write_bytes(situar(info(icono(), WBTOOL, tooltypes=TOOLTYPES), 90, 6))
    shutil.copy(raiz / "build/trasfondoprefs", caj / "TrasfondoPrefs")
    (caj / "TrasfondoPrefs.info").write_bytes(situar(info(icono_prefs(), WBTOOL), 170, 6))
    # el Amiga lee ISO-8859-1: el script y el LEEME, de UTF-8 a Latin-1
    (caj / "Instalar").write_bytes((raiz / "paquete/Instalar").read_text().encode("latin-1"))
    (caj / "Instalar.info").write_bytes(
        situar(info(instalador(), WBPROJECT, herramienta="Installer",
                    tooltypes=["APPNAME=Trasfondo", "MINUSER=AVERAGE", "DEFUSER=AVERAGE"]), 10, 6))
    (caj / "LEEME").write_bytes((raiz / "README.md").read_text().encode("latin-1", "replace"))
    (caj / "LEEME.info").write_bytes(situar(info(documento(), WBPROJECT, herramienta="SYS:Utilities/MultiView"), 250, 6))
    shutil.copy(raiz / "LICENSE", caj / "LICENSE")
    lha = raiz / f"build/trasfondo-{version}.lha"
    lha.unlink(missing_ok=True)
    subprocess.run(["/opt/amiga/bin/lha", "ao5q", str(lha), "Trasfondo", "Trasfondo.info"]
                   + [f"Trasfondo/{p.name}" for p in sorted(caj.iterdir())], cwd=dest, check=True)
    print(lha)


if __name__ == "__main__":
    main()
