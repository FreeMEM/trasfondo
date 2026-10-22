# Trasfondo como commodity

Trasfondo 0.2 se controla desde Exchange, como cualquier commodity de AmigaOS. Sigue escrito solo en Dash:
lo que falta se añade a Dash como builtins, igual que `desktop_canvas*` y `cpu_*`.

## Qué hace cada orden

| Orden | Qué hace Trasfondo |
|---|---|
| Ocultar (Hide) | Quita el panel del fondo. Sigue midiendo la CPU: al mostrarlo, la historia del último minuto está completa. |
| Mostrar (Show) | Vuelve a poner el panel. |
| Desactivar (Disable) | Quita el panel y deja de medir la CPU (`cpu_stop`). No gasta nada mientras tanto. |
| Activar (Enable) | Vuelve a medir (`cpu_start`) y pone el panel, con la historia vacía. |
| Eliminar (Kill) | Se acaba y deja el fondo como estaba. |
| Tecla rápida | Muestra u oculta el panel. Se elige con el tooltype `CX_POPKEY` (por omisión, ninguna). |

Lanzarlo otra vez lo sigue parando, como en la 0.1 (`single_instance`). Ctrl-C también.

Tooltypes estándar de commodity: `CX_PRIORITY` (prioridad del broker), `CX_POPKEY` (tecla rápida) y
`CX_POPUP` (`NO`: arranca oculto). Desde el Shell valen igual como argumentos: `trasfondo CX_POPKEY="ctrl alt t"`.

## Lo que falta en Dash

Lo que ya hay y basta: `desktop_canvas_free` y volver a llamar a `desktop_canvas` para ocultar y mostrar;
`cpu_stop` y `cpu_start` para desactivar y activar. Hay que confirmar que las dos parejas se pueden repetir
muchas veces en el mismo programa (crear, liberar, crear otra vez) sin perder memoria ni dejar ganchos puestos.

Falta:

1. **Tooltypes.** Leer un tooltype del icono del programa, con un valor por omisión. Arrancado desde el
   Shell, los mismos nombres como argumentos `NOMBRE=valor`. Sirve también para la fase 3 del plan
   (posición y colores por tooltypes).
2. **Broker de commodity.** Darse de alta en `commodities.library` con nombre, título y descripción (lo que
   enseña Exchange), con la prioridad de `CX_PRIORITY`. Que salga una sola vez en Exchange aunque se lance
   dos veces (de eso ya se encarga `single_instance`, que va antes). Debe declarar que admite mostrar y
   ocultar (`COF_SHOW_HIDE`); si no, Exchange deja esos dos botones en gris.
3. **Tecla rápida.** Poner una tecla rápida a partir de su descripción (`"ctrl alt t"`). Si la descripción
   no vale, decirlo (para avisar en la salida) en vez de fallar.
4. **Recibir las órdenes.** Una función que diga qué orden llegó: ninguna, ocultar, mostrar, desactivar,
   activar, eliminar o tecla rápida. Al desactivar y activar, el broker debe cambiar de estado él mismo
   (`ActivateCxObj`), para que Exchange lo enseñe bien y la tecla rápida no funcione mientras está
   desactivado.
5. **Esperar sin gastar.** Ahora el bucle duerme un segundo (`time_delay(50)`) y luego mira `break_check`.
   Hace falta una espera que acabe al pasar el tiempo, al llegar una orden de Exchange o al llegar Ctrl-C,
   lo que pase antes. Así la orden se cumple al momento y no al segundo siguiente.
6. **Al acabar**, el broker y la tecla rápida se quitan solos, como hace `desktop_canvas_free` con el fondo.

Los nombres y la forma de las funciones los decide Dash, con su estilo.

## Cómo se prueba

En el emulador (AmigaOS 3.2.3 y RTG), con Exchange abierto:

- Trasfondo sale en la lista con su título y descripción.
- Ocultar y Mostrar diez veces seguidas: el panel se va y vuelve, los iconos siguen intactos y la memoria
  libre no baja.
- Desactivar: el panel se va y la CPU de Trasfondo baja a 0. Activar: vuelve con la historia vacía.
- La tecla rápida oculta y muestra; desactivado, no hace nada.
- Eliminar, lanzarlo otra vez y Ctrl-C: se acaba, el fondo queda como estaba y no sale en Exchange.
- Con `CX_POPUP=NO` arranca oculto.
