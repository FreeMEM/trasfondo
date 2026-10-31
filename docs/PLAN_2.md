# Trasfondo 2.0 — borrador de diseño

Borrador del 2026-10-31. Nada decidido salvo lo que diga "decidido" (ver "Decisiones" al final).

## La idea

Trasfondo deja de ser solo un monitor en el fondo. Pasa a ser un escritorio moderno encima del Workbench de
AmigaOS 3.x, sin sustituirlo: el Workbench sigue ahí, con sus iconos y sus menús, y Trasfondo le añade:

1. **El fondo** (lo que ya hay): el monitor detrás de los iconos, sin clics.
2. **La barra**: una franja arriba con piezas (reloj, fecha, tiempo, CPU, memoria, red, temperatura,
   avisos). Cada pieza abre un panel al pulsarla.
3. **Los paneles**: el de resumen (reloj grande, calendario, tiempo, avisos) y el de ajustes rápidos
   (red, volumen, paleta clara u oscura, reiniciar, accesos a Prefs).
4. **Los avisos**: un buzón donde cualquier programa deja un aviso (por ARexx o con una orden del Shell).
5. **El dock**: lanzadores y programas abiertos, en cualquier borde, horizontal o vertical.
6. **Las ventanas**: maximizar, minimizar, encajar a media pantalla y cambiar de tamaño con facilidad, en
   las ventanas de cualquier programa.
7. **Los ajustes**: un solo programa para configurarlo todo, con buscador, que sustituye a TrasfondoPrefs.
8. **Archivos**: un gestor de ficheros entre Directory Opus y Nautilus.

## Arquitectura

Una familia de programas, no uno solo. Cada uno se arranca aparte (WBStartup) y se puede no instalar.

| Programa | Qué es | Interfaz |
|---|---|---|
| `Trasfondo` | el fondo (ya existe) y el centro: mide, guarda los avisos, reparte los datos | sin ventana |
| `TrasfondoBarra` | barra y paneles | ventana sin bordes, dibujada a mano |
| `TrasfondoDock` | el dock | ventana sin bordes, dibujada a mano |
| `TrasfondoVentanas` | atajos y gestos para las ventanas | commodity sin ventana |
| `TrasfondoAjustes` | los ajustes | ReAction |
| `Archivos` | gestor de ficheros | ReAction |
| `Avisa` | orden del Shell para dejar un aviso | ninguna |

Por qué separados: en un A1200 cada uno gasta memoria, y el usuario elige qué quiere. Si uno falla, los
demás siguen (sin protección de memoria, un fallo grave cuelga todo igual, pero los fallos leves no).

Lo que comparten:

- **Un puerto público** `TRASFONDO` (de `Trasfondo`), también con ARexx: `NOTIFY`, `GETDATA CPU`, `QUIT`...
  La barra y el dock piden ahí los datos en vez de medir otra vez.
- **Un fichero de ajustes**, `ENVARC:Trasfondo/` copiado a `ENV:`. Cada programa vigila el suyo
  (`file_notify`) y se aplica al momento.
- **Un tema**: colores, radios de esquina, fuente. Barra, paneles y dock solo en RTG (16 o 24 bits:
  esquinas redondas, sombras, transparencia). En AGA/ECS sigue solo el fondo, como hoy (decidido).

## Las piezas

### Barra

- Sustituye a la barra de título de la pantalla del Workbench: ventana sin bordes en y=0, del ancho de
  la pantalla. El botón derecho sigue abriendo los menús del Workbench o de la ventana activa.
- Piezas configurables, en tres grupos (izquierda, centro, derecha), como en la captura de niri:
  - izquierda: lista de pantallas (el equivalente de los escritorios: cada pantalla abierta), lista de
    ventanas del Workbench, menú de inicio (opcional);
  - centro: hora, fecha, tiempo, campana con el número de avisos;
  - derecha: CPU, memoria, disco, red, WiFi, temperatura de la PiStorm, ajustes rápidos.
- A comprobar: arrastrar la barra de título para bajar la pantalla (se pierde al taparla; la barra puede
  hacerlo ella).

### Paneles

- Resumen: reloj grande, calendario del mes, tiempo de ahora y de los próximos días, lista de avisos
  con "Descartar" y "Limpiar todo".
- Ajustes rápidos: usuario y nombre del Amiga, tiempo encendido, red y WiFi, volumen (si hay forma), modo
  noche (cambiar la paleta del Workbench), accesos a los Prefs del sistema, reiniciar (con aviso).
- Se cierran al pulsar fuera o con Esc.

### Tiempo

Open-Meteo por HTTPS (sin clave; Dash ya tiene TLS con AmiSSL). Lugar por nombre (su geocodificador) o
latitud y longitud. Se pregunta cada 30 minutos.

### Avisos

- Quién avisa: el propio Trasfondo (disco casi lleno, poca memoria Chip, PiStorm caliente, versión
  nueva), y cualquier programa por ARexx (`ADDRESS TRASFONDO 'NOTIFY TITLE="..." TEXT="..."'`) o con
  `Avisa "texto"`.
- Un aviso sale unos segundos en una esquina y queda en el panel de resumen.
- Botones opcionales con una orden ARexx o del Shell detrás ("Abrir", "Marcar como leído").

### Dock

- Cualquier borde, horizontal o vertical, centrado o pegado a una esquina. Ocultarse solo (opcional).
- Lanzadores: se añaden soltando un icono encima. Usa el icono `.info` del programa (y los PNG de
  icon.library 46 en 3.2).
- Programas abiertos: un punto debajo del lanzador. Saber qué ventana es de qué programa en AmigaOS no es
  directo (la tarea del puerto de la ventana); a comprobar.
- Carpetas como pila: al pulsar, abre su contenido en un panel. Papelera.

### Ventanas

Lo que pide el usuario (2026-10-31): el Workbench no deja cambiar el tamaño, minimizar ni maximizar con
facilidad.

Un sistema de ventanas propio basado en MUI solo serviría para los programas MUI (y MUI ya trae botón de
iconizar). Para que valga con cualquier programa, la propuesta es una commodity que actúe sobre la
ventana de debajo del ratón o la activa:

- Atajos de teclado (Amiga + flechas): maximizar, devolver el tamaño, encajar a la mitad o a un cuarto
  de pantalla, mandar atrás.
- Gestos de ratón: doble clic en la barra de título para maximizar; arrastrar con una tecla pulsada
  desde cualquier punto para mover o cambiar el tamaño (como en Linux con Alt).
- Minimizar: AmigaOS 3.x no tiene ese estado. Se imita escondiendo la ventana (llevarla fuera de la
  pantalla o detrás de todo) y dejándola en la lista de ventanas de la barra o en el dock.
- Respeta los límites de cada ventana (tamaño mínimo y máximo, si se puede cambiar).
- Mosaico (tiles), pedido por el usuario el 2026-10-31, en dos modos que se eligen por pantalla:
  - a mano: atajos que reparten las ventanas abiertas en columnas, en filas o en rejilla, una vez;
  - automático, como niri o i3: cada ventana nueva entra en el mosaico y las demás se reparten el sitio;
    al cerrarse una, las otras crecen. Atajos para cambiar el foco y el orden, y para sacar una ventana
    del mosaico (flotante).
  - Siempre flotan: las que no se pueden redimensionar, los requesters y las que el usuario marque por
    título o por programa.
  - El mosaico deja libres la barra y el dock.
  - Límite: sin parchear Intuition no hay aviso de "ventana nueva". La commodity mira la lista de ventanas
    cada poco (medio segundo), así que una ventana nueva se verá un instante en su sitio antes de
    colocarse. A medir en el A1200.

No se parchean funciones del sistema (nada de `SetFunction` sobre Intuition): solo se mueven y redimensionan
ventanas con las llamadas normales. Así no choca con MCP, VisualPrefs y compañía.

### Ajustes

Un programa ReAction como el de la captura (sustituye a TrasfondoPrefs, también en AGA y con 68000): lista de secciones a la izquierda (Apariencia, Barra, Piezas,
Dock, Ventanas, Fondo, Avisos, Tiempo, Archivos), buscador arriba, y al final accesos a los Prefs del
sistema (Locale, Font, ScreenMode, WBPattern...). Aquí cabe la idea pendiente de ordenar secciones
arrastrando.

### Archivos

- Una o dos columnas (como Directory Opus), con barra lateral de volúmenes y favoritos, barra de ruta,
  vista en lista o en iconos (como Nautilus).
- Menú del botón derecho según el tipo: abrir con su herramienta por defecto (la del icono o DefIcons),
  "abrir con", descomprimir (lha, lzx, zip... con xadmaster.library o las órdenes del Shell),
  reproducir, ver, renombrar, comprimir, propiedades.
- Copiar, cortar, pegar y mover, también arrastrando. Las copias en segundo plano, en una cola; el
  progreso sale en la barra y el final, como aviso.
- Buscar por nombre (con comodines) y por contenido.
- Es lo más grande de todo, más que el resto junto. Directory Opus 5 (Magellan) es de código abierto y
  corre en 3.x: mirarlo antes de diseñar.

## Qué le falta a Dash

Se añade a Dash como builtins, como siempre. A comprobar uno por uno, pero seguramente:

- Hecho (2026-10-31): ventana sin barra de título; `On RightClick`, `On Inactive` y `rmbtrap`; `cx_key_add`
  (varias teclas y botones del ratón por commodity); `wm_*` (listar las ventanas de la pantalla del Workbench
  y moverlas, redimensionarlas, traerlas delante o detrás, activarlas). En dash1 y dashc.
- Ventana siempre encima o, al menos, saber cuándo la tapan.
- AppWindow y AppIcon: soltar iconos en el dock y en Archivos.
- Menús emergentes (botón derecho), dibujados a mano: ReAction de 3.x no los trae (ver "Interfaz").
- Puerto público con mensajes propios entre programas Dash, y puerto ARexx.
- ReAction: la lista de Dash (`ra_add_listbrowser`) solo admite líneas de texto. Hacen falta columnas,
  iconos por fila, árbol (desplegar carpetas), selección múltiple, ordenar por columna, saber el clic
  derecho, y más de 4 ventanas por programa.
- Leer `.info` y dibujarlos a cualquier tamaño; DefIcons para saber el tipo de un fichero.
- xadmaster.library para descomprimir sin órdenes externas (opcional).

## Interfaz

ReAction en todo lo que es una ventana normal (Ajustes y Archivos). Barra, paneles y dock se dibujan a
mano. Sin MUI. Decidido con el usuario el 2026-10-31.

Por qué: viene con el sistema en 3.2 y 3.9 (en 3.1, ClassAct), funciona con 68000, gasta menos memoria
que MUI y Dash ya lo soporta. Así Ajustes y Archivos funcionan también en AGA.

Comprobado en el NDK 3.2 (autodocs y notas de versión), 2026-10-31:

| Lo que hace falta | ¿Lo trae ReAction de 3.2? | Plan |
|---|---|---|
| Lista con columnas, iconos, árbol, selección múltiple, ordenar | Sí: `listbrowser.gadget` (`LBNCA_Image`, `LBFLG_HASCHILDREN`, `LISTBROWSER_MultiSelect`, `LBCIA_Sortable`) | Pedir a Dash que lo exponga |
| Menú del botón derecho | No: `WINDOW_PopupGadget` y `WMHI_POPUPMENU` son solo de OS4 | Ventana con `WA_RMBTrap` y el menú dibujado a mano, el mismo que en la barra |
| Arrastrar ficheros entre listas | No: la lista solo arrastra para seleccionar y para mover columnas | A mano: con el botón pulsado sobre una selección se dibuja lo arrastrado y al soltar se mira sobre qué lista cae. Desde el Workbench hacia Archivos, AppWindow (`WINDOW_AppWindow`) |
| Vista de iconos | No hay clase para eso | Zona de dibujo propia (`ra_add_drawing_area`) con los `.info` |

Las tres que faltan se hacen a mano, sin MUI. El menú emergente y el arrastre se comparten con la barra y
el dock, que ya se dibujan a mano.

## Lo que ya existe (a investigar en Aminet antes de diseñar cada pieza)

Directory Opus 4 y 5, Scalos (sustituye al Workbench), ToolManager (docks), AmiStart (menú de inicio),
MCP y VisualPrefs (botones de ventana), PopupMenu (menús emergentes). Cada uno cubre un trozo; ninguno
lo junta todo con un aspecto moderno. Esa es la diferencia que buscamos.

## Estado (2026-10-31)

En la rama `trasfondo-2`, probado solo en FS-UAE (68040, uaegfx, Workbench 3.2.3), con dash1 y dashc:

- Hecho, primera versión: barra (`src/barra.dash`), panel de resumen (`panel.dash`), tiempo (`tiempo.dash`,
  `https.dash`), avisos (`avisa.dash`, `aviso.dash`, `avisos.dash`), ajustes rápidos (`rapido.dash`), dock
  (`dock.dash`) y ventanas (`ventanas.dash`: maximizar, mitades, restaurar, mosaico a mano y automático,
  mover y redimensionar con Alt y el ratón).
- Lo compartido, por ahora en `ENV:` (`Trasfondo.tiempo`, `Trasfondo.avisos`, `Trasfondo.dock`), no por un
  puerto: el puerto `TRASFONDO` sigue pendiente.
- Sabido que falla: la barra y el dock son ventanas normales (otra ventana las tapa); la barra se queda la
  activación al pulsarla; la barra y Trasfondo miden la CPU a la vez y uno de los dos sale mal; los textos,
  solo en inglés; el mosaico automático mira las ventanas cada medio segundo (se ve la nueva en su sitio un
  momento).
- Capturas: `tools/vista.py` (FS-UAE con RTG, clics, teclas y órdenes por guion).

## Orden propuesto

1. Base común: puerto `TRASFONDO`, ajustes en `ENV:`, tema, y separar la medida del dibujo en el código
   que ya hay.
2. Barra con reloj, fecha, CPU, memoria y red (reutiliza la medida de 0.11), y panel de resumen.
3. Avisos (`NOTIFY`, `Avisa`, campana) y tiempo.
4. Ventanas (commodity).
5. Dock.
6. Ajustes (sustituye a TrasfondoPrefs).
7. Archivos.

## Decisiones

Decidido con el usuario (2026-10-31):

- Barra, paneles y dock, solo con RTG. En AGA/ECS queda el fondo de siempre.
- Archivos va dentro de Trasfondo: un programa más de la familia, en este repositorio.
- Ventanas: una commodity que vale para todas, sin parchear el sistema, con mosaico a mano y automático.
- La barra de Trasfondo sustituye a la de título del Workbench.
- ReAction en todas las ventanas normales, sin MUI (ver "Interfaz").

Abiertas:

- Arrastrar la pantalla hacia abajo con la barra tapando la de título.
