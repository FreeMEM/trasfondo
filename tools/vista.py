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
PROGRAMAS = {"barra": "TrasfondoBarra", "panel": "TrasfondoPanel", "aviso": "TrasfondoAviso", "avisa": "Avisa", "rapido": "TrasfondoRapido", "dock": "TrasfondoDock", "ventanas": "TrasfondoVentanas"}


def compilar(nombre, fuente=None):
    env = dict(os.environ, PYTHONPATH=str(DASH))
    subprocess.run([str(DASH / "dash"), fuente or f"src/{nombre}.dash", "-o", f"build/{nombre}", "-q"], cwd=RAIZ,
                   env=env, check=True)


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
        elif p[0] == "aqui":
            lineas += [f"    input_click({p[1]}, {p[2]}, 0)"]
        elif p[0] == "mover":
            lineas += [f"    input_move_screen({p[1]}, {p[2]}, 0)"]
        elif p[0] == "mantener":
            lineas += ["    window_activate(0)", "    time_delay(10)", f"    input_move({p[1]}, {p[2]} - 500)",
                       "    time_delay(50)", "    input_button(1, true)", "    time_delay(75)",
                       "    input_button(1, false)"]
        elif p[0] == "mantener_hw":
            # el botón izquierdo "de verdad": la línea /FIR0 del CIA-A puesta a 0 como salida (DDRA), como si se
            # pulsara el ratón; lo ven mouse_button y gameport.device (input.device, Intuition) igual que un ratón
            lineas += ["    window_activate(0)", "    time_delay(10)", f"    input_move({p[1]}, {p[2]} - 500)",
                       "    time_delay(50)", "    poke_byte(0xBFE001, peek_byte(0xBFE001) & 0xBF)",
                       "    poke_byte(0xBFE201, peek_byte(0xBFE201) | 0x40)", "    time_delay(150)",
                       "    poke_byte(0xBFE201, peek_byte(0xBFE201) & 0xBF)"]
        elif p[0] == "abrir":
            lineas += [f'    ok = wb_open("{p[1]}")']
        elif p[0] == "arrastrar":
            # pulsar en (x1, y1), llevarlo a (x2, y2) con el botón abajo y soltar: un icono del Workbench
            x1, y1, x2, y2 = p[1]
            lineas += ["    window_activate(0)", "    time_delay(10)", f"    input_move({x1}, {y1} - 500)",
                       "    time_delay(25)", "    input_button(1, true)", "    time_delay(2)",
                       f"    input_move_screen({x1 + 8}, {y1 + 8}, 1)", "    time_delay(10)",
                       f"    input_move_screen({x2}, {y2}, 1)", "    time_delay(25)", "    input_button(1, false)"]
        elif p[0] == "menus":
            lineas += [f"    input_move_screen({p[1]}, {p[2]}, 0)", "    input_button(2, true)", "    time_delay(150)",
                       "    input_button(2, false)"]
        elif p[0] == "derecho":
            lineas += ["    window_activate(0)", "    time_delay(10)", f"    input_move({p[1]}, {p[2]} - 500)",
                       "    time_delay(40)", "    input_button(2, true)", "    time_delay(5)",
                       "    input_button(2, false)"]
        elif p[0] == "pulsar":
            lineas += [f"    input_move_screen({p[1]}, {p[2]}, 0)", "    input_button(1, true)", "    time_delay(5)",
                       "    input_button(1, false)"]
        elif p[0] == "tecla":
            lineas += [f"    input_key({p[1]}, {p[2]})"]
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
    ap.add_argument("--aqui", action="append", dest="pasos", type=lambda v: ("aqui", v),
                    help="X,Y,SEGUNDOS: clic desde la esquina de la ventana activa, sin activar otra")
    ap.add_argument("--mover", action="append", dest="pasos", type=lambda v: ("mover", v),
                    help="X,Y,SEGUNDOS: lleva el puntero ahí, sin pulsar")
    ap.add_argument("--pulsar", action="append", dest="pasos", type=lambda v: ("pulsar", v),
                    help="X,Y,SEGUNDOS: lleva el puntero ahí (pantalla) y pulsa, sin activar otra ventana antes")
    ap.add_argument("--mantener", action="append", dest="pasos", type=lambda v: ("mantener", v),
                    help="X,Y,SEGUNDOS: salta ahí (activa antes el guion) y mantiene el botón izquierdo 1,5 s")
    ap.add_argument("--mantener-hw", action="append", dest="pasos", type=lambda v: ("mantener_hw", v),
                    help="X,Y,SEGUNDOS: como --mantener, pero con el botón del puerto del ratón (CIA), 3 s")
    ap.add_argument("--menus", action="append", dest="pasos", type=lambda v: ("menus", v),
                    help="X,Y,SEGUNDOS: lleva el puntero ahí y mantiene el botón derecho 3 s (los menús de Intuition)")
    ap.add_argument("--abrir", action="append", dest="pasos", type=lambda v: ("abrir", v),
                    help="SEGUNDOS:RUTA: abre ese cajón en el Workbench")
    ap.add_argument("--arrastrar", action="append", dest="pasos", type=lambda v: ("arrastrar", v),
                    help="X1,Y1,X2,Y2,SEGUNDOS: arrastra con el botón izquierdo (un icono del Workbench al dock)")
    ap.add_argument("--derecho", action="append", dest="pasos", type=lambda v: ("derecho", v),
                    help="X,Y,SEGUNDOS: salta ahí (activa antes el guion) y pulsa el botón derecho")
    ap.add_argument("--tecla", action="append", dest="pasos", type=lambda v: ("tecla", v),
                    help="CODIGO,CALIFICADORES,SEGUNDOS: una tecla en bruto (0x14 la T; 2 Ctrl + 4 Alt...)")
    ap.add_argument("--barra", default="CIUDAD=Mijas", help="argumentos de la barra")
    ap.add_argument("--ventanas", default=None, help="arranca TrasfondoVentanas con estos argumentos, y tres "
                    "ventanas de prueba (tools/ventanitas.dash)")
    ap.add_argument("--dock", default=None, help="arranca el dock con estos argumentos (POSICION=ABAJO)")
    ap.add_argument("--fondo", default=None, help="arranca también el fondo (Trasfondo, de build/release) con estos "
                    "argumentos; TrasfondoPrefs queda en DH0: y ENV:Trasfondo.cajon apunta ahí")
    ap.add_argument("--copiar", action="append", default=[], help="fichero:Nombre, copiado a DH0:Nombre")
    ap.add_argument("--carpeta", action="append", default=[], help="carpeta:Nombre, copiada entera a DH0:Nombre")
    ap.add_argument("--fijar", action="append", default=[], help="una ruta más en el dock (DH0:Trasfondo), al final")
    ap.add_argument("--inicio", action="append", default=[], help="una línea más para la Startup-Sequence, tras LoadWB")
    a = ap.parse_args()
    for n in PROGRAMAS:
        compilar(n)
    if a.ventanas is not None:
        compilar("ventanitas", "tools/ventanitas.dash")
    pasos = []
    for tipo, v in a.pasos:
        if tipo == "arrastrar":
            x1, y1, x2, y2, seg = v.split(",")
            pasos.append(("arrastrar", (int(x1), int(y1), int(x2), int(y2)), float(seg)))
        elif tipo == "abrir":
            seg, ruta = v.split(":", 1)
            pasos.append(("abrir", ruta, float(seg)))
        elif tipo in ("clic", "mover", "aqui", "pulsar", "mantener", "mantener_hw", "derecho", "menus"):
            x, y, seg = v.split(",")
            pasos.append((tipo, int(x), int(y), float(seg)))
        elif tipo == "tecla":
            c, q, seg = v.split(",")
            pasos.append(("tecla", int(c, 0), int(q), float(seg)))
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
        if a.fondo is not None:
            shutil.copy(RAIZ / "build/release/trasfondo", hd / "Trasfondo")
            shutil.copy(RAIZ / "build/release/TrasfondoPrefs", hd / "TrasfondoPrefs")
            extra += f"Echo DH0: >ENV:Trasfondo.cajon\nRun >NIL: DH0:Trasfondo {a.fondo}\n"
        extra += "".join(l + "\n" for l in a.inicio)
        for c in a.copiar:
            f, n = c.split(":", 1)
            shutil.copy(RAIZ / f, hd / n)
        for c in a.carpeta:
            f, n = c.split(":", 1)
            shutil.copytree(RAIZ / f, hd / n, dirs_exist_ok=True)
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
            lista += "SYS:System/Shell\nSYS:Prefs\n" + "".join(f + "\n" for f in a.fijar)
            (hd / "dock.txt").write_text(lista)
            extra += f"Copy DH0:dock.txt ENV:Trasfondo.dock QUIET\nRun >NIL: DH0:TrasfondoDock {a.dock}\n"
        if a.ventanas is not None:
            shutil.copy(RAIZ / "build" / "ventanitas", hd / "Ventanitas")
            extra += f"Run >NIL: DH0:TrasfondoVentanas {a.ventanas}\nRun >NIL: DH0:Ventanitas\n"
        t = t.replace("C:LoadWB\n", "C:LoadWB\n" + extra, 1)
        ss.write_text(t)

    if not KS:
        sys.exit("vista.py: falta el Kickstart 3.2 de A1200 en $KS o $DASH_KICKSTART_32")
    os.chdir(RAIZ)
    run_programs([guion(pasos)], timeout=max(c[0] for c in capturas) + 60, kickstart=KS, system=str(SYS), workbench=True,
                 extra_config=MACHINES["rtg"]["config"] + "bsdsocket_library = 1\n", screenshot=capturas, on_disk=en_disco, keep=os.environ.get("GUARDA"))


if __name__ == "__main__":
    main()
