#!/usr/bin/env python3
"""Los catálogos de Trasfondo: los textos (en inglés, los del programa) y sus traducciones.

    DASH=~/.cache/ratonera-dash python3 tools/catalogos.py

Saca de nuevo catalogos/Trasfondo.cd de los tr() de src/, pone al día cada catalogos/<idioma>.ct (guarda lo
traducido; lo nuevo queda vacío y sale en inglés) y hace build/Catalogs/<idioma>/Trasfondo.catalog (el castellano, también en build/Catalogs/spanish). El
nombre del cajón va en Latin-1, como lo espera el Amiga (español).
"""

import os
import subprocess
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
# el mismo idioma, con el nombre que le da AmigaOS 3.2 (el 3.1 y el 3.9 lo llaman "español")
OTROS_NOMBRES = {"español": ["spanish"]}
catalogo = Path(os.environ.get("DASH", Path.home() / ".cache/ratonera-dash")) / "tools/catalogo.py"


def correr(*args):
    subprocess.run([sys.executable, str(catalogo), *map(str, args)], check=True)


def main():
    cd = raiz / "catalogos/Trasfondo.cd"
    correr("cd", raiz / "src/trasfondo.dash", raiz / "src/trasfondoprefs.dash", "-o", cd)
    for ct in sorted((raiz / "catalogos").glob("*.ct")):
        idioma = ct.stem
        correr("ct", cd, "--language", idioma, "--name", "Trasfondo.catalog", "--version", "1.0",
               "--update", ct, "-o", ct)
        lineas = ct.read_text().splitlines()
        vacios = sum(1 for i, l in enumerate(lineas[:-1]) if l.startswith("MSG_") and lineas[i + 1] == "")
        if vacios:
            print(f"{ct.name}: {vacios} textos sin traducir (salen en inglés)")
        for nombre in [idioma] + OTROS_NOMBRES.get(idioma, []):
            fuente = ct
            if nombre != idioma:                           # el mismo, con el nombre del idioma cambiado
                fuente = raiz / "build/otro.ct"
                fuente.write_text(ct.read_text().replace(f"## language {idioma}\n", f"## language {nombre}\n"))
            hecho = raiz / "build/Trasfondo.catalog"      # (catalogo.py no sabe escribir un nombre en Latin-1)
            correr("catalog", fuente, "-o", hecho)
            cajon = os.path.join(os.fsencode(raiz / "build/Catalogs"), nombre.encode("latin-1"))
            os.makedirs(cajon, exist_ok=True)
            os.replace(hecho, os.path.join(cajon, b"Trasfondo.catalog"))


if __name__ == "__main__":
    main()
