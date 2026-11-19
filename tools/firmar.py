#!/usr/bin/env python3
"""Las firmas de una versión publicada, para pegarlas en las notas de la release de GitHub (el botón Actualizar de
Trasfondo no baja nada sin ellas; aviso de seguridad del 31/10/2026: con la cuenta de GitHub robada se podían repartir ejecutables
falsos). Escribe build/release/FIRMAS.txt:

    [sha256 <64 cifras> <fichero>]      una por cada fichero suelto de build/release (no el .lha)
    [firma <128 cifras>]                Ed25519 de "Trasfondo <versión>\\n" y "<cifras> <fichero>\\n" de cada línea

    python3 tools/firmar.py 2.9.9

La clave privada está en ~/.config/freemem/firma-actualizaciones (no va al repo); la pública, en src/actualizar.dash
(FIRMA_CLAVE). Es la misma que firma Tachyon.
"""
import hashlib
import sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519

CLAVE = Path.home() / ".config" / "freemem" / "firma-actualizaciones"


def firmas(version: str, rel: Path) -> str:
    k = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(CLAVE.read_text().strip()))
    lineas = []
    for f in sorted(rel.iterdir()):
        if f.is_file() and not f.name.endswith(".lha") and f.name != "FIRMAS.txt":
            lineas.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()} {f.name}")
    mensaje = f"Trasfondo {version}\n" + "".join(x + "\n" for x in lineas)
    firma = k.sign(mensaje.encode())
    k.public_key().verify(firma, mensaje.encode())
    return "".join(f"[sha256 {x}]\n" for x in lineas) + f"[firma {firma.hex()}]\n"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    rel = Path(__file__).resolve().parent.parent / "build" / "release"
    texto = firmas(sys.argv[1].lstrip("v"), rel)
    (rel / "FIRMAS.txt").write_text(texto)
    print(texto, end="")


if __name__ == "__main__":
    main()
