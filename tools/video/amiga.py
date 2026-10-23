"""Lo que se ve dentro del Amiga emulado, leído de su memoria por el socket de Amiberry: Intuition, sus
pantallas, ventanas y gadgets, y dónde está el puntero."""
from amiberry import orden


def rd(addr, w=4):
    r = orden("READ_MEM", addr, w)
    assert r.startswith("OK"), r
    v = int(r.split("\t")[1])
    if w == 2 and v >= 0x8000:
        v -= 0x10000
    return v


def cadena(addr, maximo=80):
    s = b""
    while addr and len(s) < maximo:
        palabra = rd(addr, 4).to_bytes(4, "big")
        for c in palabra:
            if c == 0:
                return s.decode("latin-1")
            s += bytes([c])
        addr += 4
    return s.decode("latin-1")


def biblioteca(nombre):
    exec_base = rd(4)
    n = rd(exec_base + 378)                     # LibList.lh_Head
    while rd(n):                                # ln_Succ
        if cadena(rd(n + 10)) == nombre:
            return n
        n = rd(n)
    return 0


_ib = None


def ibase():
    global _ib
    if not _ib:
        _ib = biblioteca("intuition.library")
    return _ib


def pantalla():
    """La primera pantalla (la de delante)."""
    return rd(ibase() + 60)


def puntero():
    s = pantalla()
    return rd(s + 18, 2), rd(s + 16, 2)        # MouseX, MouseY de la pantalla


def ventanas():
    """[(dirección, título, x, y, ancho, alto)] de la pantalla de delante."""
    r = []
    w = rd(pantalla() + 4)
    while w:
        r.append((w, cadena(rd(w + 32)), rd(w + 4, 2), rd(w + 6, 2), rd(w + 8, 2), rd(w + 10, 2)))
        w = rd(w)
    return r


def bordes(w):
    """(izquierda, arriba) del borde de una ventana: donde empieza su interior."""
    return rd(w + 54, 1), rd(w + 55, 1)


def ventana(titulo):
    """La primera ventana cuyo título empieza así: (dirección, título, x, y, ancho, alto), o None. Solo lee
    las letras que hacen falta: cada lectura por el socket cuesta un cuadro."""
    w = rd(pantalla() + 4)
    while w:
        if cadena(rd(w + 32), len(titulo)).startswith(titulo):
            return (w, titulo, rd(w + 4, 2), rd(w + 6, 2), rd(w + 8, 2), rd(w + 10, 2))
        w = rd(w)
    return None


def gadgets(w):
    """[(x, y, ancho, alto, texto)] de los gadgets de una ventana, en coordenadas de la pantalla."""
    r = []
    wx, wy = rd(w + 4, 2), rd(w + 6, 2)
    gzz = rd(w + 24) & 0x400                    # WFLG_GIMMEZEROZERO: cuentan desde dentro del borde
    bl, bt = bordes(w) if gzz else (0, 0)
    g = rd(w + 62)                              # FirstGadget
    while g:
        x, y, an, al = rd(g + 4, 2), rd(g + 6, 2), rd(g + 8, 2), rd(g + 10, 2)
        it = rd(g + 26)                         # GadgetText
        texto = cadena(rd(it + 12)) if it else ""
        r.append((wx + bl + x, wy + bt + y, an, al, texto))
        g = rd(g)
    return r


def tareas():
    """Los nombres de las tareas que esperan o están listas."""
    eb = rd(4)
    r = []
    for lista in (406, 420):                    # TaskReady, TaskWait
        n = rd(eb + lista)
        for _ in range(500):                    # una tarea que cambia de cola al leerla: sin vueltas eternas
            if not rd(n):
                break
            r.append(cadena(rd(n + 10)))
            n = rd(n)
    return r
