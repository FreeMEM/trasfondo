# Trasfondo — plan

Un "top" gráfico para el Workbench de AmigaOS 3.x, pintado en el fondo de pantalla: en otro plano,
detrás de los iconos y de las ventanas, sin recibir clics. Escrito en Dash.

## Lo que ya hay (investigado el 2026-10-20)

- **atop** 1.0.1 (Aminet `util/moni/atop`, Samuel Kielek, subido el 2026-10-19): top para OS 3.x, OS4 y
  MorphOS. CPU, memoria, volúmenes, red y tareas con su % de CPU. Tiene un modo widget (`WIDGET=YES`):
  una ventana de fondo (backdrop) sin entrada. Sus límites en 68k, según su `atop.doc`:
  - la CPU es una estimación por el refresco vertical, gruesa;
  - la transparencia es una foto del fondo tomada al arrancar ("not a live layer"): lo que cambie
    después detrás no se ve;
  - es una ventana: tapa los iconos del escritorio que caigan debajo.
- **PM** (Michael Sinz, `util/moni/PM`): mide la CPU de forma exacta con los ganchos de cambio de tarea
  de exec 2.04 y el reloj EClock. Fuentes incluidas: la referencia para medir.
- Otros monitores de `util/moni` (TaskPie, PerfMonitor, AmigaLoad...) abren su propia ventana.

En qué nos diferenciamos: de verdad en el plano del fondo (los iconos quedan encima y el fondo de
pantalla es el real, no una foto) y CPU por tarea exacta.

## Cómo (idea a comprobar)

- **Dibujar en el fondo**: el Workbench pinta el fondo de su ventana con un gancho de relleno de la capa
  (`InstallLayerHook`, layers.library 39). Trasfondo pone el suyo: llama al anterior (el fondo de
  pantalla de WBPattern o el color 0) y encima copia sus gráficos. Los iconos los pinta el Workbench
  después, encima.
  - Modo backdrop del Workbench (iconos en el escritorio): gancho en la capa de su ventana de fondo.
  - Sin backdrop: el fondo es el de la pantalla (`InstallLayerInfoHook`) y no hay iconos encima.
- **Refrescar** cada segundo sin borrar los iconos. Dos maneras probadas (ver Resultados):
  - *ventana*: abrir y cerrar al momento una ventana de fondo sin relleno sobre la zona. Intuition
    repinta la zona con nuestro gancho (los iconos se borran) y el Workbench vuelve a pintarlos.
    Parpadea.
  - *máscara* (la elegida): con la capa del Workbench bloqueada, leer la zona de la pantalla; lo que no
    coincide con el panel de antes es un icono (o algo que pintó el Workbench); copiar el panel nuevo
    solo fuera de eso (`BltMaskBitMapRastPort`). Los iconos no se tocan nunca. Límite: un píxel de icono
    del mismo color que el panel de antes en ese punto se toma por fondo y se pisa.
- **Doble buffer**: los gráficos se dibujan en un mapa de bits aparte y el gancho solo copia, porque el
  gancho lo llama cualquier tarea que provoque un repintado.
- **Medir**: CPU total y por tarea con los ganchos de exec (como PM); memoria Chip y Fast; volúmenes;
  quizá red.
- **Sin clics**: no hay ventana propia que pueda recibirlos. Se cierra como commodity (Exchange) o
  lanzándolo otra vez.

## Resultados de la prueba (2026-10-20)

`tests/prueba_fondo.dash` en FS-UAE, A1200, Kickstart y Workbench 3.2.3 (`sys32`), pantalla de
640x256 a 4 colores, panel de 300x90 encima de los iconos RAM Disk y DH0.

- El Workbench ya estaba en backdrop; su ventana de fondo es de refresco simple y ya tenía un gancho
  de relleno propio. Cambiarlo por el nuestro y devolverlo al final funciona.
- Los iconos quedan encima del panel (capturas).
- *ventana*: unos 37 ms por refresco. Entre que el gancho borra los iconos y el Workbench los vuelve
  a pintar pasan unos 6 ms, y hasta 158 ms con otra tarea ocupando la CPU. Una captura cogió un icono a
  medio pintar: el parpadeo se ve.
- *máscara*: unos 45 ms por refresco. Tras cada uno, los únicos píxeles del panel distintos de lo
  esperado son exactamente los de los iconos (764 de 764) y ningún píxel de icono cambia.
- La herramienta de capturas de `emu_run.py` lee la pantalla despacio: las capturas tomadas mientras
  algo pinta salen rotas (media zona a medias). No son fallos del panel; la cuenta de píxeles manda.

Sin probar todavía: fondo de pantalla de verdad (WBPattern con imagen), Kickstart 3.1, pantallas RTG
(la máscara trabaja por planos y en RTG no los hay), Workbench sin backdrop (el código que lo pide por
el menú no llegó a usarse), otras ventanas encima del panel, cambio de preferencias mientras corre.

## Fases

1. Prueba en el emulador (`tests/prueba_fondo.dash`): gancho en el fondo del Workbench en modo
   backdrop, un panel que se actualiza cada segundo, y comprobar en capturas que los iconos siguen
   encima y cuánto parpadean.
2. CPU exacta, total y por tarea.
3. Paneles: CPU, memoria, tareas, volúmenes. Colores y posición por tooltypes.
4. Fondos de pantalla de WBPattern, cambios de preferencias (el Workbench puede volver a poner su
   gancho), salir limpio.
5. Commodity, paquete para Aminet.

Lo que haga falta en Dash (ganchos con registros, por ejemplo) se añade a Dash.
