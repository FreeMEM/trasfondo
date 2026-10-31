#!/usr/bin/env python3
"""Capturas de las piezas de Trasfondo 2.0 en FS-UAE con RTG (A1200, 68040, uaegfx, Workbench 3.2.3).

Compila los programas, los deja en DH0: con su nombre, arranca la barra, y un guion Dash pulsa y lanza
órdenes cuando se le diga. Solo para ver cómo queda. Usa la red del PC (bsdsocket de FS-UAE): se corre con
flock /run/user/1000/dash-emu-red.lock si hay otras pruebas con red a la vez.

    KS=kick32.rom tools/vista.py [SEG:]captura.png... [--clic X,Y,SEG] [--orden "SEG:Avisa ..."] [--barra "CIUDAD=Mijas"]
"""
import argparse, os, re, shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DASH = Path(os.environ.get("DASH", Path.home() / "Projects/FreeMEMLang"))
KS = os.environ.get("KS") or os.environ.get("DASH_KICKSTART_32")   # un Kickstart 3.2 de A1200
SYS = Path(os.environ.get("DASH_EMU_SYS_32_RTG", Path.home() / ".cache/dash-emu/sys32rtg32"))   # Workbench 3.2 con uaegfx
ICONOS = [str(Path.home() / p) for p in ("Amiberry/LHA/Tachyon.info", "Amiberry/LHA/dashweb.info",
          ".cache/dash-mui/x/MUI/Demos/Clock.info", "m68k-amigaos-gcc/projects/NDK3.2/MuManual/Manual.info",
          "m68k-amigaos-gcc/projects/NDK3.2/Examples/ARexx.info")]
PROGRAMAS = {"barra": "TrasfondoBarra", "panel": "TrasfondoPanel", "aviso": "TrasfondoAviso", "avisa": "Avisa", "rapido": "TrasfondoRapido", "dock": "TrasfondoDock"}


def compilar(nombre):
    env = dict(os.environ, PYTHONPATH=str(DASH))
    subprocess.run([str(DASH / "dash"), f"src/{nombre}.dash", "-o", f"build/{nombre}", "-q"], cwd=RAIZ, env=env,
                   check=True)


def guion(pasos):
    """Un programa Dash que espera y hace cada paso: ("clic", x, y, seg) pulsa en (x, y) de la pantalla, ("orden",
    texto, seg) lanza una orden; seg, lo que espera antes, desde el paso anterior. Abre una ventana pequeña
    abajo a la izquierda para que los clics cuenten desde un sitio conocido (input_click mide desde la esquina
    de la ventana activa)."""
    lineas = ["Window G", '    title "guion"', "    width 60", "    height 30", "    left 0", "    top 500",
              "end", "Main", "    G.open", "    time_delay(50)"]
    for p in pasos:
        lineas.append(f"    time_delay({int(p[-1] * 50)})")
        if p[0] == "clic":
            lineas += ["    window_activate(0)", "    time_delay(10)", f"    input_click({p[1]}, {p[2]} - 500, 0)"]
        else:
            lineas.append("    run_program(" + '"' + p[1].replace('"', '\\"') + '"' + ")")
    lineas += ["    time_delay(100000)", "end"]
    g = RAIZ / "build" / "guion.dash"
    g.write_text("\n".join(lineas) + "\n")
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("captura", nargs="+", help="SEGUNDOS:fichero.png (o fichero.png, a los --seg)")
    ap.add_argument("--seg", type=float, default=25)
    ap.add_argument("--clic", action="append", default=[], dest="pasos", type=lambda v: ("clic", v),
                    help="X,Y,SEGUNDOS desde el paso anterior")
    ap.add_argument("--orden", action="append", dest="pasos", type=lambda v: ("orden", v),
                    help="SEGUNDOS:orden (Avisa TITULO=...), desde el paso anterior")
    ap.add_argument("--barra", default="CIUDAD=Mijas", help="argumentos de la barra")
    ap.add_argument("--dock", default=None, help="arranca el dock con estos argumentos (POSICION=ABAJO)")
    a = ap.parse_args()
    for n in PROGRAMAS:
        compilar(n)
    pasos = []
    for tipo, v in a.pasos:
        if tipo == "clic":
            x, y, seg = v.split(",")
            pasos.append(("clic", int(x), int(y), float(seg)))
        else:
            seg, orden = v.split(":", 1)
            pasos.append(("orden", orden, float(seg)))
    capturas = []
    for c in a.captura:
        seg, _, f = c.rpartition(":")
        capturas.append((float(seg) if seg else a.seg, f))
    sys.path.insert(0, str(DASH / "tools"))
    from emu_run import run_programs, MACHINES

    def en_disco(hd):
        for n, nombre in PROGRAMAS.items():
            shutil.copy(RAIZ / "build" / n, hd / nombre)
        ss = hd / "S" / "Startup-Sequence"
        t = ss.read_text()
        extra = f"Run >NIL: DH0:TrasfondoBarra {a.barra}\n"
        if a.dock is not None:
            # unos lanzadores de prueba: iconos de verdad (los que haya en ICONOS) con un programa cualquiera
            apps = hd / "Apps"
            apps.mkdir(exist_ok=True)
            lista = ""
            for ico in ICONOS:
                if Path(ico).exists():
                    n = Path(ico).stem
                    shutil.copy(ico, apps / f"{n}.info")
                    shutil.copy(RAIZ / "build" / "avisa", apps / n)
                    lista += f"DH0:Apps/{n}\n"
            lista += "SYS:System/Shell\nSYS:Prefs\n"
            (hd / "dock.txt").write_text(lista)
            extra += f"Copy DH0:dock.txt ENV:Trasfondo.dock QUIET\nRun >NIL: DH0:TrasfondoDock {a.dock}\n"
        t = t.replace("C:LoadWB\n", "C:LoadWB\n" + extra, 1)
        ss.write_text(t)

    if not KS:
        sys.exit("vista.py: falta el Kickstart 3.2 de A1200 en $KS o $DASH_KICKSTART_32")
    os.chdir(RAIZ)
    run_programs([guion(pasos)], timeout=max(c[0] for c in capturas) + 60, kickstart=KS, system=str(SYS), workbench=True,
                 extra_config=MACHINES["rtg"]["config"] + "bsdsocket_library = 1\n", screenshot=capturas, on_disk=en_disco, keep=os.environ.get("GUARDA"))


if __name__ == "__main__":
    main()
