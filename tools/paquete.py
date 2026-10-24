#!/usr/bin/env python3
"""El paquete de Trasfondo para Aminet y GitHub: el cajón Trasfondo con sus iconos y el .lha.

    python3 tools/paquete.py 0.3        →  build/paquete/Trasfondo/...  y  build/trasfondo-0.3.lha

Necesita build/trasfondo y build/trasfondoprefs compilados, los catálogos hechos (tools/catalogos.py) y el lha de 68k (/opt/amiga/bin/lha) para que
el archivo guarde bien los atributos.
"""

import os
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
    # los catálogos (tools/catalogos.py), con el nombre del idioma en Latin-1: Catalogs/español/Trasfondo.catalog.
    # Junto a trasfondo valen tal cual (PROGDIR:Catalogs); el instalador los copia además a LOCALE:Catalogs
    cats = os.fsencode(raiz / "build/Catalogs")
    for idioma in os.listdir(cats):
        os.makedirs(os.path.join(os.fsencode(caj), b"Catalogs", idioma))
        shutil.copy(os.path.join(cats, idioma, b"Trasfondo.catalog"),
                    os.path.join(os.fsencode(caj), b"Catalogs", idioma, b"Trasfondo.catalog"))
    lha = raiz / f"build/trasfondo-{version}.lha"
    lha.unlink(missing_ok=True)
    ficheros = [os.path.relpath(os.path.join(d, f), os.fsencode(dest))
                for d, _, fs in os.walk(os.fsencode(caj)) for f in fs]
    subprocess.run([b"/opt/amiga/bin/lha", b"ao5q", b"--system-kanji-code=latin1", b"--archive-kanji-code=latin1", os.fsencode(lha), b"Trasfondo", b"Trasfondo.info"]
                   + sorted(ficheros), cwd=dest, check=True)
    print(lha)


if __name__ == "__main__":
    main()
