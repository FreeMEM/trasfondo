#!/usr/bin/env python3
"""El paquete de Trasfondo 2.0 para Aminet y GitHub: el cajón Trasfondo con sus piezas, sus iconos, el
instalador y el .lha.

    DASH=~/Projects/FreeMEMLang/.worktrees/trasfondo-2 python3 tools/paquete.py 2.0
        →  build/paquete/Trasfondo/...  y  build/trasfondo-2.0.lha

Compila cada pieza con el Dash de $DASH (./dash, Dash 2.0) y hace los catálogos (tools/catalogos.py). Necesita el
lha de 68k (/opt/amiga/bin/lha) para que el archivo guarde bien los atributos.
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

DASH = Path(os.environ.get("DASH", Path.home() / "Projects/FreeMEMLang"))
# fuente → nombre en el Amiga; las que arrancan con el Workbench llevan icono de herramienta y de arranque
PIEZAS = {"trasfondo": "Trasfondo", "barra": "TrasfondoBarra", "panel": "TrasfondoPanel", "aviso": "TrasfondoAviso",
          "rapido": "TrasfondoRapido", "dock": "TrasfondoDock", "ventanas": "TrasfondoVentanas",
          "trasfondoprefs": "TrasfondoPrefs", "avisa": "Avisa"}
CON_ICONO = ["Trasfondo", "TrasfondoBarra", "TrasfondoDock", "TrasfondoVentanas"]


def situar(icono, x, y):
    """El icono en (x, y) de su cajón (do_CurrentX/Y; sin esto, el Workbench lo coloca donde quiere)."""
    b = bytearray(icono)
    b[58:62] = x.to_bytes(4, "big")
    b[62:66] = y.to_bytes(4, "big")
    return bytes(b)


def compilar(dest):
    env = dict(os.environ, PYTHONPATH=str(DASH))
    for fuente, nombre in PIEZAS.items():
        r = subprocess.run([str(DASH / "dash"), str(raiz / "src" / f"{fuente}.dash"), "-o", str(dest / nombre)],
                           cwd=raiz, env=env, capture_output=True, text=True)
        if r.returncode or "dash1" in r.stdout + r.stderr:
            sys.exit(f"paquete: {fuente}.dash no compila con Dash 2.0:\n{r.stdout}{r.stderr}")
        (dest / nombre).chmod(0o755)


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "0.0"
    subprocess.run([sys.executable, str(raiz / "tools/catalogos.py")], check=True, env=dict(os.environ, DASH=str(DASH)),
                   stdout=subprocess.DEVNULL)
    dest = raiz / "build/paquete"
    shutil.rmtree(dest, ignore_errors=True)
    caj = dest / "Trasfondo"
    caj.mkdir(parents=True)
    compilar(caj)
    (dest / "Trasfondo.info").write_bytes(situar(info(cajon(), WBDRAWER), 10, 6))
    (caj / "Trasfondo.info").write_bytes(situar(info(icono(), WBTOOL, tooltypes=TOOLTYPES), 90, 6))
    for i, nombre in enumerate(CON_ICONO[1:]):
        (caj / f"{nombre}.info").write_bytes(situar(info(icono(), WBTOOL), 90 + 80 * (i + 1), 6))
    (caj / "TrasfondoPrefs.info").write_bytes(situar(info(icono_prefs(), WBTOOL), 410, 6))
    # los iconos de proyecto de SYS:WBStartup (su herramienta la pone el instalador, con la ruta donde quedó)
    (caj / "Arranque").mkdir()
    for nombre in CON_ICONO:
        (caj / "Arranque" / f"{nombre}.info").write_bytes(info(icono(), WBPROJECT, herramienta=nombre, tooltypes=["DONOTWAIT"]))
    # el Amiga lee ISO-8859-1: el script y el LEEME, de UTF-8 a Latin-1
    (caj / "Instalar").write_bytes((raiz / "paquete/Instalar").read_text().encode("latin-1"))
    (caj / "Instalar.info").write_bytes(
        situar(info(instalador(), WBPROJECT, herramienta="Installer",
                    tooltypes=["APPNAME=Trasfondo", "MINUSER=AVERAGE", "DEFUSER=AVERAGE"]), 10, 6))
    (caj / "LEEME").write_bytes((raiz / "README.es.md").read_text().encode("latin-1", "replace"))
    (caj / "LEEME.info").write_bytes(situar(info(documento(), WBPROJECT, herramienta="SYS:Utilities/MultiView"), 10, 60))
    shutil.copy(raiz / "LICENSE", caj / "LICENSE")
    # los catálogos (tools/catalogos.py), con el nombre del idioma en Latin-1: Catalogs/español/Trasfondo.catalog.
    # Junto a las piezas valen tal cual (PROGDIR:Catalogs); el instalador los copia además a LOCALE:Catalogs
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
