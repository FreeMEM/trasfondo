#!/usr/bin/env python3
"""El icono de Workbench de Trasfondo (.info clásico, 4 colores), con el generador de iconos de dashweb.

    python3 tools/icono.py build/trasfondo.info
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "Projects/dashweb/tools"))
from iconos_wb import Lienzo, info, GRIS, NEGRO, BLANCO, AZUL, WBTOOL   # noqa: E402


def icono():
    """Un escritorio con un panel de barras en una esquina."""
    l = Lienzo(40, 26)
    l.rect(0, 0, 39, 25, NEGRO)
    l.rect(1, 1, 38, 24, AZUL)
    l.rect(3, 4, 7, 7, BLANCO)          # dos iconos del escritorio
    l.rect(3, 12, 7, 15, BLANCO)
    l.rect(18, 3, 36, 22, NEGRO)        # el panel
    for i, alto in enumerate((4, 9, 6, 13, 8, 15)):
        x = 20 + i * 3
        l.rect(x, 20 - alto, x + 1, 20, BLANCO)
    return l


if __name__ == "__main__":
    # los tooltypes de commodity; la tecla rápida, entre paréntesis: apagada hasta que se le quiten
    Path(sys.argv[1]).write_bytes(info(icono(), WBTOOL,
                                       tooltypes=["CX_PRIORITY=0", "CX_POPUP=YES", "(CX_POPKEY=ctrl alt t)"]))
