# El vídeo de Trasfondo

Cómo se graba el vídeo de instalación y uso, en Coffin R65 (Amiberry), sin tocar el Coffin de verdad.

- `preparar.py`: copia el disco de Coffin con reflink (btrfs: no gasta sitio), pone el paquete en un
  `Traspaso:` propio, arranca Amiberry sin ventana (`SDL_VIDEODRIVER=offscreen`) y deja el agente en marcha.
- `guion.py <carpeta>`: la toma. Maneja el Amiga por el socket de control de Amiberry
  (`$XDG_RUNTIME_DIR/amiberry.sock`: `SEND_MOUSE`, `SCREENSHOT`, `READ_MEM`, `WRITE_MEM`) y marca subtítulos,
  capítulos, clics y recuadros con la hora de la toma. `rodaje.py` saca 25 capturas por segundo.
- `montar.py <carpeta> <salida.mp4>`: el vídeo de 1920x1080 (rótulos azul Workbench 1.3 con Topaz y bola
  Boing, la pantalla del Amiga a escala entera con barrido, subtítulos quemados y en pista, capítulos).
- `agente.c`: dentro del Amiga, lo que el socket no hace: teclas (`SEND_KEY` solo vale para las acciones de
  Amiberry, no para teclas del Amiga) y lanzar programas. Su buzón es un puerto público "agente"; se esconde
  de los medidores de CPU con un gancho de cambio de tarea vacío.

Lo aprendido: cada lectura de memoria por el socket cuesta un cuadro (20 ms), así que las posiciones de los
gadgets van medidas de antemano; el OCR no lee los nombres de los iconos sobre el fondo con trama, por eso
los iconos del paquete llevan su sitio; las ventanas de Dash son GimmeZeroZero (sus gadgets cuentan desde
dentro del borde); para arrastrar, cada `SEND_MOUSE` debe llevar el botón pulsado.

Fuentes: Topaz de [rewtnull/amigafonts](https://github.com/rewtnull/amigafonts) (GPL con excepción de
fuentes), en `~/.cache/video-trasfondo/fuentes`.
