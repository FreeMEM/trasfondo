#!/usr/bin/env python3
"""Capturas de las piezas de Trasfondo 2.0 en FS-UAE con RTG (A1200, 68040, uaegfx, Workbench 3.2.3).

Compila los programas como Dash, pero con WA_Title NULL en las ventanas de título "" (Dash aún pasa "" y
Intuition pinta una barra de título), los deja en DH0: con su nombre, arranca la barra, y un guion Dash
pulsa donde se le diga. Solo para ver cómo queda.

    KS=kick32.rom tools/vista.py captura.png [--clic X,Y,SEG]... [--seg SEG] [--barra "CIUDAD=Mijas"]
"""
import argparse, os, re, shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DASH = Path(os.environ.get("DASH", Path.home() / "Projects/FreeMEMLang"))
KS = os.environ.get("KS") or os.environ.get("DASH_KICKSTART_32")   # un Kickstart 3.2 de A1200
SYS = Path(os.environ.get("DASH_EMU_SYS_32_RTG", Path.home() / ".cache/dash-emu/sys32rtg32"))   # Workbench 3.2 con uaegfx
PROGRAMAS = {"barra": "TrasfondoBarra", "panel": "TrasfondoPanel"}


def compilar(nombre):
    c = RAIZ / "build" / f"{nombre}.c"
    env = dict(os.environ, PYTHONPATH=str(DASH), PATH="/opt/amiga/bin:" + os.environ["PATH"])
    subprocess.run([sys.executable, "-m", "compiler.main", f"src/{nombre}.dash", "-o", str(c)],
                   cwd=RAIZ, env=env, check=True, stdout=subprocess.DEVNULL)
    t = c.read_text(encoding="latin-1")
    t = t.replace('WA_Title, (ULONG)""', "WA_Title, (ULONG)NULL")
    t = t.replace("WA_Title, (ULONG)title,", "WA_Title, (ULONG)(*title ? title : NULL),")
    c.write_text(t, encoding="latin-1")
    sys.path.insert(0, str(DASH))
    from compiler.cflags import opt_flags, mui_flags, amissl_flags, link_flags, cpu_flags
    from compiler.clibs import libraries_for
    gcc = "/opt/amiga/bin/m68k-amigaos-gcc"
    inc, ficheros = link_flags([t])
    orden = ([gcc, "-noixemul", "-I/opt/amiga/m68k-amigaos/ndk-include", "-Ibuild", "-L/opt/amiga/m68k-amigaos/lib"]
             + opt_flags(False, False) + mui_flags([t]) + amissl_flags([t]) + inc + cpu_flags(None, False)
             + [str(c)] + ficheros + libraries_for([t], gcc, cpu_flags(None, False), "build")
             + ["-o", str(RAIZ / "build" / nombre), "-lm"])
    subprocess.run(orden, cwd=RAIZ, env=env, check=True)


def guion(clics):
    """Un programa Dash que espera y pulsa: una ventana pequeña abajo a la izquierda, para que los clics
    cuenten desde un sitio conocido (input_click mide desde la esquina de la ventana activa)."""
    lineas = ["Window G", '    title "guion"', "    width 60", "    height 30", "    left 0", "    top 500",
              "end", "Main", "    G.open", "    time_delay(50)"]
    for x, y, espera in clics:
        lineas += [f"    time_delay({int(espera * 50)})", "    window_activate(0)", "    time_delay(10)",
                   f"    input_click({x}, {y} - 500, 0)"]
    lineas += ["    time_delay(100000)", "end"]
    p = RAIZ / "build" / "guion.dash"
    p.write_text("\n".join(lineas) + "\n")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("captura")
    ap.add_argument("--seg", type=float, default=25)
    ap.add_argument("--clic", action="append", default=[], help="X,Y,SEGUNDOS desde el anterior")
    ap.add_argument("--barra", default="CIUDAD=Mijas", help="argumentos de la barra")
    a = ap.parse_args()
    for n in PROGRAMAS:
        compilar(n)
    clics = [tuple(int(v) if i < 2 else float(v) for i, v in enumerate(c.split(","))) for c in a.clic]
    sys.path.insert(0, str(DASH / "tools"))
    from emu_run import run_programs, MACHINES

    def en_disco(hd):
        for n, nombre in PROGRAMAS.items():
            shutil.copy(RAIZ / "build" / n, hd / nombre)
        ss = hd / "S" / "Startup-Sequence"
        t = ss.read_text()
        t = t.replace("C:LoadWB\n", f"C:LoadWB\nRun >NIL: DH0:TrasfondoBarra {a.barra}\n", 1)
        ss.write_text(t)

    os.chdir(RAIZ)
    run_programs([guion(clics)], timeout=a.seg + 15, kickstart=KS, system=str(SYS), workbench=True,
                 extra_config=MACHINES["rtg"]["config"] + "bsdsocket_library = 1\n", screenshot=(a.seg, a.captura), on_disk=en_disco)


if __name__ == "__main__":
    main()
