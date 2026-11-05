"""El LEEME del paquete: el README en Markdown pasado a texto llano de 80 columnas, para leerlo en el Amiga
(MultiView, Ed, More) sin desplazarse de lado. Idea de Ferrán García.

    from leeme import texto80
    texto80(Path("README.es.md").read_text())

Párrafos y listas se cortan a 80; los bloques de código quedan como están, con sangría; las tablas pasan a
"columna 1" y debajo, con sangría, el resto; los enlaces quedan como "texto (dirección)"; las imágenes, fuera.
"""
import re
import textwrap

ANCHO = 80


def _limpiar(t):
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)                 # imágenes
    t = re.sub(r"\[\s*\]\([^)]*\)", "", t)                      # (y el enlace que las rodeaba)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: m.group(1) if m.group(1) == m.group(2) or m.group(2).startswith("#")
               else f"{m.group(1)} ({m.group(2)})", t)        # enlaces
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)                    # negrita
    t = re.sub(r"(?<![\w*])\*([^*\s][^*]*)\*(?![\w*])", r"\1", t)  # cursiva
    t = re.sub(r"`([^`]+)`", r"\1", t)                          # código en línea
    t = re.sub(r"<[^>]+>", "", t)                               # HTML suelto
    return t.strip()


def _cortar(t, sangria="", primera=None):
    return textwrap.fill(t, ANCHO, initial_indent=primera if primera is not None else sangria,
                         subsequent_indent=sangria, break_long_words=False, break_on_hyphens=False)


def texto80(md):
    sal = []
    parrafo = []
    lineas = md.splitlines()
    i = 0

    def soltar():
        if parrafo:
            sal.append(_cortar(_limpiar(" ".join(parrafo))))
            sal.append("")
            parrafo.clear()

    while i < len(lineas):
        l = lineas[i]
        s = l.strip()
        if s.startswith("```"):                                   # código: tal cual, con sangría
            soltar()
            i += 1
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                sal.append("    " + lineas[i].rstrip())
                i += 1
            sal.append("")
        elif s.startswith("|"):                                    # tabla
            soltar()
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                celdas = [_limpiar(c) for c in lineas[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in celdas if c):
                    filas.append(celdas)
                i += 1
            for n, f in enumerate(filas):
                if n == 0 and len(filas) > 1:
                    continue                                       # (los títulos de las columnas)
                sal.append(_cortar(f[0]))
                if len(f) > 1 and " ".join(f[1:]).strip():
                    sal.append(_cortar(" - ".join(c for c in f[1:] if c), "    "))
            sal.append("")
            continue
        elif s.startswith("#"):                                    # título
            soltar()
            nivel = len(s) - len(s.lstrip("#"))
            t = _limpiar(s.lstrip("#"))
            if t:
                sal.append(t.upper() if nivel <= 2 else t)
                sal.append(("=" if nivel == 1 else "-") * min(len(t), ANCHO))
                sal.append("")
        elif re.match(r"\s*([-*+]|\d+\.)\s", l):                  # elemento de lista (y sus líneas de después)
            soltar()
            m = re.match(r"(\s*)([-*+]|\d+\.)\s+(.*)", l)
            base = len(m.group(1).expandtabs())
            marca = "-" if m.group(2) in "-*+" else m.group(2)
            texto = [m.group(3)]
            i += 1
            while (i < len(lineas) and lineas[i].strip() and not re.match(r"\s*([-*+]|\d+\.)\s", lineas[i])
                   and not lineas[i].strip().startswith(("```", "|", "#"))
                   and len(lineas[i]) - len(lineas[i].lstrip()) > base):
                texto.append(lineas[i].strip())
                i += 1
            sangria = " " * (base + len(marca) + 1)
            sal.append(_cortar(_limpiar(" ".join(texto)), sangria, " " * base + marca + " "))
            if i >= len(lineas) or not lineas[i].strip():
                sal.append("")
            continue
        elif not s:
            soltar()
        elif s.startswith(">"):
            parrafo.append(s.lstrip("> "))
        else:
            parrafo.append(s)
        i += 1
    soltar()
    texto = "\n".join(sal)
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip() + "\n"
    return texto


if __name__ == "__main__":
    import sys
    print(texto80(open(sys.argv[1]).read()), end="")
