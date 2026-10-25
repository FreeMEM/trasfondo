# Discos, red y WiFi

*[English](DISCOS_Y_RED.en.md) | Castellano*

Hecho en Trasfondo 0.2 con los builtins `disks_*`, `net_if*` y `wifi_*` de Dash (PR #17). Discos probado en el
emulador; red y WiFi, sin probar con Roadshow ni con WiFi de verdad.

Tres paneles nuevos para Trasfondo, pedidos por usuarios que vienen de NewMeter:

- **Discos**: cada volumen montado, con su capacidad y cuánto está lleno.
- **Red**: lo que entra y sale por segundo.
- **WiFi**: la calidad de la señal, y si la red está conectada o no.

Como el resto, en Dash puro: lo que falta se añade a Dash como builtins.

## Lo que hay que evitar (los fallos de NewMeter)

- **Colgar el sistema** al preguntar por la WiFi. Ninguna consulta puede esperar sin límite: si el
  dispositivo no contesta en un tiempo corto (medio segundo, por ejemplo), se abandona esa lectura
  (`AbortIO`) y el panel lo dice ("sin respuesta").
- **No enterarse de que se desconectó la red.** Cada lectura se hace de nuevo, sin dar por buenos datos ni
  dispositivos abiertos de antes. Si el interfaz desaparece o el dispositivo se cierra, el panel lo dice, y
  vuelve a mostrar datos cuando la red vuelve. Sin tener que cerrar Trasfondo.
- **Ventana transparente con restos de otras ventanas.** Trasfondo no tiene ese problema: pinta en el fondo
  de verdad, no en una ventana.

## Discos

Para cada volumen montado con disco dentro: nombre, tamaño total, ocupado y libre (`Info()` sobre el
volumen). Sin pedir "Inserta el volumen" (`dos_requesters(false)` ya existe) y sin quedarse esperando a
un volumen lento o de red: si no contesta, se salta.

Builtins que faltan: la lista de volúmenes montados y, de cada uno, tamaño y libre.

## Red

Bytes recibidos y enviados de cada interfaz, para sacar la velocidad restando una lectura de la anterior.
Con Roadshow, `ObtainInterfaceList` y `QueryInterfaceTagList` de `bsdsocket.library` dan los interfaces,
su estado y sus contadores de bytes. Con otras pilas (AmiTCP, Miami) que no lo tengan, el panel no sale.

Builtins que faltan: la lista de interfaces, su estado (conectado o no) y sus bytes de entrada y salida.

## WiFi

La calidad de la señal se pide al driver SANA-II del interfaz (su nombre y unidad, de Roadshow) con la
orden de calidad de señal de la extensión inalámbrica de SANA-II (la que da `prism2.device` y otros
drivers de Neil Cafferkey: nivel de señal y de ruido). Si el driver no la tiene, el panel enseña solo
conectado o desconectado.

Builtin que falta: la calidad de la señal de un interfaz, con un tiempo máximo de espera.

Los nombres exactos de etiquetas y órdenes hay que comprobarlos en los includes de Roadshow y de SANA-II.

## Cómo se prueba

- Discos: en el emulador, con varios volúmenes (DH0, RAM, un disquete y la unidad de disquete vacía). Los
  números deben coincidir con los de `Info` del Shell, y la unidad vacía no debe pedir disco.
- Red: en el emulador con red y Roadshow, bajando un fichero: la velocidad debe cuadrar con la de la
  descarga. Sin Roadshow, el panel no sale y nada falla.
- Desconectar la red en marcha (en el emulador, quitar el interfaz con `NetShutdown`, o bajarlo): el panel
  lo dice al momento, nada se cuelga, y al volver la red vuelve a dar datos.
- WiFi: el emulador no tiene WiFi. Hay que probarlo en un Amiga real con tarjeta WiFi (`prism2.device`).
