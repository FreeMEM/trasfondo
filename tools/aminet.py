#!/usr/bin/env python3
"""Trasfondo en Aminet (util/moni): build/aminet/Trasfondo.lha y Trasfondo.readme, y con --subir por FTP a
main.aminet.net/new. Usa tools/aminet.py de Tachyon (~/Projects/tachyon: comprobaciones de Aminet, remitente). Sube
build/trasfondo-X.Y.Z.lha tal cual (el de la release). Aminet tenía la 2.9.5; la 2.9.13 se subió el 21/11/2026 (lo
pidió el usuario).

    python3 tools/aminet.py 2.9.13 [--subir]
"""
import ftplib
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "Projects/tachyon/tools"))
import aminet as m  # noqa: E402

perfil = {
    "nombre": "Trasfondo",
    "cabecera": [
        ("Short", "Resource monitor on the WB backdrop"),
        ("Author", "FreeMEM"),
        ("Uploader", m.SUBIDOR),
        ("Type", "util/moni"),
        ("Version", None),
        ("Requires", "Workbench running, any 68k"),
        ("Architecture", "m68k-amigaos >= 3.0.0"),
        ("Distribution", "Aminet"),
        ("Kurz", "Systemmonitor auf dem WB-Hintergrund"),
    ],
    "descripcion": """\
Trasfondo is a resource monitor for the Workbench (AmigaOS 3.x), written in
Dash (https://github.com/FreeMEM/dash): a graphical "top" painted on the
backdrop itself, behind the icons and the windows.

In the top right corner of the desktop it shows the date and time, CPU usage
and its history, the Raspberry Pi temperature on a PiStorm (Emu68), free
Chip and Fast memory, the six tasks using the most CPU, the mounted disks,
and the network traffic (and WiFi signal) with any TCP/IP stack.

It also brings optional pieces, each one a separate program:
- TrasfondoBarra: a bar with the time, date, weather, CPU and memory, with a
  panel (clock, calendar, weather, notifications) and quick settings.
- Notifications: the Avisa command and an ARexx port (TRASFONDO).
- Screenshots to PNG with a key.
- TrasfondoDock: a dock with the open programs and the ones you pin; drop a
  Workbench icon on it to pin it.
- TrasfondoVentanas: snapping, maximizing and tiling windows, Alt+Tab,
  without patching the system.
- TrasfondoArchivos: a file manager.
- TrasfondoPrefs: the preferences for all of them.

It speaks English out of the box and Spanish with its catalog.

Requirements:
- AmigaOS 3.0 or later (Kickstart 39), with the Workbench running.
- Any 68k: 68000 code, no FPU needed.
- Native chipset (OCS, ECS, AGA) or a graphics card (CyberGraphX or
  Picasso96).
- About 1.9 MB on disk with every piece; the backdrop takes 136 KB of memory.

Installation: unpack the archive and double-click "Instalar" (the
installer). It asks where to put the Trasfondo drawer and which pieces start
with the Workbench. It also updates itself with one click, and since 2.9.9
it only installs updates signed by its author.

Source code (MIT licence), issues and every release:
https://github.com/FreeMEM/trasfondo
Website: https://trasfondo.freemem.space

What's new since 2.9.5
----------------------
- TrasfondoPrefs stays open: Save and Use apply the changes without closing
  the window.
- The dock menu (hold down an icon) works again.
- Updates are signed: the Update button only installs versions signed by
  the author.
- Tooltypes on a project icon (in WBStartup or a document) now count.
- Trasfondo no longer fills WBStartup with its icons; TrasfondoPrefs offers
  to move it to its own drawer.
- Network traffic with AmiNetXDuo, the panel with a DOpus desktop, the dock
  stays hidden behind other screens, and Exchange answers at once even with
  a slow WiFi.
""",
}
ver = sys.argv[1]
raiz = Path(__file__).resolve().parent.parent
lha = raiz / f"build/trasfondo-{ver}.lha"
texto = m.readme(perfil, ver, "")
errores = m.comprobar(perfil, texto, lha)
if errores:
    sys.exit("No vale para Aminet:\n  " + "\n  ".join(errores))
dest = raiz / "build/aminet"
dest.mkdir(parents=True, exist_ok=True)
(dest / "Trasfondo.readme").write_bytes(texto.encode("latin-1"))
shutil.copyfile(lha, dest / "Trasfondo.lha")
print(texto)
print(dest, (dest / "Trasfondo.lha").stat().st_size)
if "--subir" in sys.argv:
    with ftplib.FTP(m.SERVIDOR, timeout=120) as ftp:
        ftp.login("anonymous", m.SUBIDOR.split()[0])
        ftp.cwd("new")
        for f in ("Trasfondo.lha", "Trasfondo.readme"):
            with open(dest / f, "rb") as h:
                print(ftp.storbinary(f"STOR {f}", h), f)
