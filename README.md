# Trasfondo

Monitor de recursos para el Workbench de **Commodore Amiga** (AmigaOS 3.x): un "top" gráfico pintado en el
propio fondo de pantalla, detrás de los iconos y las ventanas. No se puede pulsar: solo está ahí, de fondo.

Arriba a la derecha del escritorio enseña:

- La CPU en uso y su historia del último minuto.
- La memoria Chip y Fast libre.
- Las seis tareas que más CPU toman.
- Los discos montados: cuánto está lleno cada uno y su tamaño.
- La red: lo que entra y sale por segundo en cada interfaz, y la señal de la WiFi si la tarjeta la da.

Se actualiza cada segundo. Los iconos quedan por encima del panel, como siempre.

![Trasfondo en Coffin R65, sobre un fondo de pantalla con imagen](docs/captura-coffin.png)

En AmigaOS 3.2.3, pantalla AGA de 640x256:

![Trasfondo en el Workbench de AmigaOS 3.2, pantalla AGA de 640x256](docs/captura-aga.png)

En una tarjeta gráfica (RTG), a 1024x768 y 32 bits de color (parte de arriba de la pantalla):

![Trasfondo en el Workbench de AmigaOS 3.2 con RTG a 1024x768](docs/captura-rtg.png)

## Escrito en Dash

Trasfondo está escrito entero en [Dash](https://github.com/FreeMEM/dash), un lenguaje de alto nivel para
Amiga que se traduce a C y se compila a un ejecutable nativo de 68k. No lleva C a mano: todo el programa
son unas 130 líneas de Dash en [src/trasfondo.dash](src/trasfondo.dash).

Lo que Dash no sabía hacer se le añadió como funciones propias del lenguaje (builtins):

- `desktop_canvas`, `desktop_canvas_on_draw`, `desktop_canvas_update`: pintar en el fondo del Workbench.
- `cpu_start`, `cpu_sample`, `cpu_total`, `cpu_task_name`, `cpu_task_load`: la CPU total y la de cada tarea.
- `single_instance` y `break_check`: una sola copia en marcha, y pararla con Ctrl-C.

Así, cualquier otro programa en Dash puede usarlas también.

## Requisitos

- **AmigaOS 3.0 o posterior** (Kickstart 39). Usa funciones de `graphics.library` y `layers.library` que
  llegaron con la versión 39.
- **Workbench en marcha**: el panel se pinta en su fondo.
- **Cualquier 68k**: el ejecutable es código de 68000 y no usa FPU.
- **Chipset nativo (OCS, ECS, AGA) o tarjeta gráfica (RTG)**. Con RTG usa `cybergraphics.library` o
  `Picasso96API.library` si están.
- **Memoria**: el ejecutable ocupa 52 KB.
- **Red y WiFi: Roadshow.** Con otra pila TCP/IP (AmiTCP, Miami), esa parte del panel no sale. La señal
  de la WiFi la tiene que dar el driver de la tarjeta (`prism2.device` y otros de Neil Cafferkey la dan).

Dónde se ha probado:

| Sistema | Máquina | Pantalla |
|---|---|---|
| AmigaOS 3.2.3 | A1200 emulado (FS-UAE), 68020 | AGA, 640x256, 4 colores |
| AmigaOS 3.2.3 | A1200 emulado (FS-UAE), 68040 | RTG (uaegfx), 1024x768, 32 bits |
| Coffin R65 | Amiberry, 68040 | RTG, 1024x768, fondo con imagen |

La parte de red y WiFi no se ha probado aún con Roadshow ni con una tarjeta WiFi de verdad: el emulador
no las tiene.

Sin probar todavía: AmigaOS 3.0, 3.1 y 3.9, un 68000 real, OCS/ECS y el Workbench sin ventana de fondo
(backdrop).

## Instalación y uso

1. Descomprime `trasfondo-0.1.lha` (de la página de
   [releases](https://github.com/FreeMEM/trasfondo/releases)) en cualquier cajón.
2. Lánzalo con doble clic, o desde el Shell con `run trasfondo`.
3. Para pararlo, lánzalo otra vez, o pulsa Ctrl-C en su Shell. El fondo queda como estaba.

Para que arranque solo con el Workbench, copia `trasfondo` y `trasfondo.info` a `SYS:WBStartup` (sin
probar todavía).

### Desde Exchange

Trasfondo es una commodity: sale en Exchange (`SYS:Tools/Commodities/Exchange`).

| Botón | Qué hace |
|---|---|
| Ocultar | Quita el panel. Sigue midiendo: al mostrarlo, la historia de la CPU está completa. |
| Mostrar | Vuelve a poner el panel. |
| Desactivar | Quita el panel y deja de medir. No gasta nada mientras tanto. |
| Activar | Vuelve a medir, con la historia vacía. |
| Eliminar | Lo cierra y deja el fondo como estaba. |

### Tooltypes

Se cambian en el icono (Información, en el menú Iconos) o se dan como argumentos en el Shell
(`run trasfondo CX_POPKEY="ctrl alt t"`).

| Tooltype | Qué hace |
|---|---|
| `CX_POPKEY=ctrl alt t` | Tecla rápida para ocultar y mostrar el panel. En el icono viene entre paréntesis, apagada: quítaselos para usarla. |
| `CX_POPUP=NO` | Arranca oculto. |
| `CX_PRIORITY=0` | Prioridad de la commodity. |

## Cómo funciona

El Workbench rellena su fondo con una función propia (un "gancho" de la capa). Trasfondo pone la suya:
primero llama a la del Workbench, que pinta el fondo de siempre, y luego copia encima el panel. Los
iconos los pinta el Workbench después, así que quedan por encima.

Cada segundo el panel se refresca sin borrar los iconos: se lee la zona de la pantalla, lo que ha
cambiado respecto al panel anterior es un icono, y el panel nuevo se copia solo fuera de eso.

La CPU de cada tarea se mide con los ganchos de cambio de tarea de exec, como hace PM. No es una
estimación: es el tiempo real que cada tarea pasa en la CPU.

## Límites conocidos

- La posición, los colores y lo que se enseña aún no se pueden cambiar (vendrán por tooltypes).
- Si un píxel de un icono coincide en color con el panel anterior en ese punto, se toma por fondo y el
  panel lo pisa hasta que el Workbench vuelva a pintar el icono.
- Después de pararlo lanzándolo otra vez, la siguiente vez que se arranca no enseña el panel. Pasa
  también en la 0.1. Es un fallo de Dash, ya avisado. Mientras, páralo desde Exchange (Eliminar) o con
  Ctrl-C: así sí vuelve a salir.

## Compilar

Hace falta Dash y su compilador cruzado (`m68k-amigaos-gcc`). Desde la raíz de este repositorio:

```bash
DASH=/ruta/a/dash
PYTHONPATH=$DASH $DASH/dash src/trasfondo.dash -o build/trasfondo
```

El icono se genera con `tools/icono.py`, que usa el generador de iconos de dashweb.

## Plan

Lo que viene (más paneles, posición y colores por tooltypes, paquete para Aminet) está en [docs/PLAN.md](docs/PLAN.md).

## Licencia

MIT (ver [LICENSE](LICENSE)).
