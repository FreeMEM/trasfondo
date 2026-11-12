# Ventanas modernas y explorador de archivos: plan y bitácora

Encargo del usuario (2026-11-12, por Tachyon2): "controles que mejoren la experiencia y que lo acerquen a un modo
moderno de trabajar con ventanas y también un explorador de archivos en condiciones, moderno y que permita hacer
copias con ficheros y borrados y movimientos, etc, todo lo que permite un nautilus o un opus5". Pidió estudiar muy
bien el UX. Se hace en la rama `ventanas-modernas` (worktree `.worktrees/ventanas`), sin tocar `src/barra.dash`.
Nada hacia fuera (push, release, web, Telegram) sin el usuario.

## 1. Estudio del UX

### Lo que hace bueno a un gestor de ventanas moderno

| Gesto | Windows 10/11 | macOS 14 | KDE Plasma | GNOME | Para Trasfondo |
|---|---|---|---|---|---|
| Maximizar | doble clic en título, botón | doble clic (zoom), botón verde | doble clic, botón | doble clic, botón | doble clic en la barra de título |
| Encajar a media pantalla | arrastrar al borde izq/der, vista previa translúcida | (14: arrastrar al borde con Opción) | arrastrar al borde, vista previa | arrastrar al borde, vista previa | arrastrar al borde con un marco de vista previa |
| Maximizar arrastrando | arrastrar al borde de arriba | — | borde de arriba | borde de arriba | borde de arriba |
| Cuartos | arrastrar a una esquina | — | esquinas | — | esquinas (cuarto de pantalla) |
| Volver al tamaño de antes | arrastrar una encajada fuera del borde | — | igual | igual | al arrastrarla otra vez, recupera su tamaño bajo el puntero |
| Menú de ventana | Alt+Espacio, clic dcho. en título | — | Alt+F3, clic dcho. en título | Alt+Espacio | clic central en la barra de título y una tecla |
| Cambiar de ventana | Alt+Tab con lista, soltar Alt elige | Cmd+Tab (programas) | Alt+Tab | Alt+Tab | Alt+Tab: lista con icono/título, Tab avanza, Mayús+Tab vuelve, soltar Alt elige, Esc cancela |
| Lista de ventanas | barra de tareas | Dock | panel | Actividades | en la barra de Trasfondo, un menú "Ventanas" |
| Mover desde cualquier punto | — | — | Alt+arrastrar | Super+arrastrar | ya está (Alt+botón izq.) |

Principios que se sacan de ahí:

1. **Lo directo con el ratón primero, las teclas para quien las quiera.** El usuario medio arrastra y hace doble
   clic; no aprende atajos.
2. **Vista previa antes de soltar**: al llegar al borde se ve dónde quedará; si te arrepientes, te alejas del borde.
   Nada se hace por sorpresa.
3. **Todo se deshace**: una ventana encajada o maximizada recuerda su tamaño de antes (ya lo hace TrasfondoVentanas).
4. **No romper lo de siempre del Amiga**: el botón derecho es de los menús, y el doble clic en un gadget es de su
   programa. Solo se mira la barra de título, y solo la parte que no tiene gadgets.
5. **Sin parchear el sistema**: commodity que observa los eventos (no se los come salvo los suyos) y mueve ventanas
   con las funciones de Intuition. Si algo no se puede sin parche, se dice y se deja.

### Límites del Amiga que cambian el diseño

- **Arrastre de Intuition con contorno (3.1)**: mientras se arrastra una ventana, Intuition bloquea las capas
  (layers) y dibuja un contorno. No se puede abrir ni pintar otra ventana hasta soltar: la vista previa durante el
  arrastre normal no es posible sin pintar debajo de Intuition. Solución: al soltar en un borde, encajar (como
  Windows 7 sin vista previa) y, en la opción "movimiento propio", hacer el arrastre Trasfondo mismo (ventana opaca,
  como el Alt+arrastrar de ahora), con vista previa. Decidir con capturas qué se ve mejor.
- **Minimizar no existe en 3.1** (3.2 tiene iconificar solo para programas que lo piden). Lo más parecido: al fondo
  (ya está) o encoger a la barra de título (`ZipWindow`, `wm_zip`).
- **Cerrar una ventana ajena**: solo su programa puede. Se puede pulsar su botón de cerrar por él (un clic simulado
  en el gadget de cierre), que es lo que haría el usuario.
- **Botones nuevos en la barra de título de otros**: necesitan pintar en ventanas ajenas o parchear Intuition. Se
  deja para el final, como opción, y solo si se ve estable.

### El explorador: qué toma de cada uno

| | Nautilus (GNOME Files) | Directory Opus 5 | Finder | Dolphin | Para TrasfondoArchivos |
|---|---|---|---|---|---|
| Disposición | barra lateral + una vista; pestañas | dos listers (origen/destino) + botonera | barra lateral + vista; pestañas | lateral + vista, dividir en dos (F3) | lateral (discos, asignaciones, favoritos, papelera) + vista; F3 divide en dos paneles |
| Vistas | iconos / lista | lista con columnas, iconos | iconos / lista / columnas | iconos / detalles / compacta | iconos (los .info de cada fichero) y lista con columnas (nombre, tamaño, fecha, tipo, comentario) |
| Ruta | barra de ruta en botones, Ctrl+L la escribe | campo de ruta | barra de ruta | migas + editable | migas que se pulsan; clic en ellas o Ctrl+L para escribirla |
| Seleccionar | clic, Ctrl+clic, Mayús+clic, lazo | clic y arrastrar sobre la lista | igual | igual | lo mismo, con lazo en iconos |
| Copiar/mover | Ctrl+C/X/V, arrastrar (Mayús mueve) | botones Copiar/Mover a la otra lista | arrastrar (Opción copia) | arrastrar con menú | Amiga+C/X/V, arrastrar (mismo disco: mover; otro: copiar; Mayús cambia), F5 copiar y F6 mover al otro panel |
| Progreso | panel de operaciones con barra, pausa y cancelar | ventana de progreso | barra en el icono | aviso con barra | ventana de progreso en segundo plano: fichero actual, total, velocidad, cancelar; varias a la vez en cola |
| Conflictos | "Reemplazar / Saltar / Renombrar / para todos" | igual | igual | igual | igual, con "para todos" |
| Borrar | a la papelera; Mayús+Supr borra del todo | borra (pregunta) | papelera | papelera | papelera por volumen (`.Papelera` en la raíz) con restaurar y vaciar; Mayús+Supr del todo con pregunta |
| Renombrar | F2 en sitio | campo | Return | F2 | F2 en el sitio, con el nombre sin la extensión elegido |
| Abrir | doble clic, con el programa por defecto | doble clic, tipos de fichero | igual | igual | doble clic: herramienta por defecto del .info (`wb_open`) |
| Buscar | escribir filtra | filtro | campo | Ctrl+F filtra | escribir filtra la carpeta; Ctrl+F busca en subcarpetas |
| Deshacer | Ctrl+Z deshace copiar/mover/renombrar/borrar | — | Cmd+Z | Ctrl+Z | Amiga+Z para renombrar, mover y borrar a la papelera |
| Miniaturas | sí | visor | sí | sí | de las imágenes (datatypes), en segundo plano, después |

Principios para el explorador:

1. **Nunca bloquear la ventana**: leer carpetas grandes y copiar van en una tarea aparte; se puede seguir navegando.
2. **Nada se pierde sin querer**: borrar va a la papelera; reemplazar pregunta; una copia a medias se borra al
   cancelar; los permisos, la fecha y el comentario se copian iguales.
3. **Lo que ve el Workbench, igual**: los iconos `.info` van con su fichero (copiar, mover, renombrar y borrar los
   dos), y la vista de iconos usa los suyos.
4. **Teclado completo**: flechas, Return abre, Retroceso sube, Tab cambia de panel, escribir busca.
5. **Rápido en un 68020**: listas virtuales (solo se pinta lo que se ve), carpetas leídas una vez y avisos de cambios
   (`file_notify`) para refrescar.

## 2. Plan por partes

**Parte 1: TrasfondoVentanas moderno** (sin parches)
- 1a. Doble clic en la barra de título (zona sin gadgets): maximiza / vuelve.
- 1b. Encajar al soltar una ventana arrastrada contra un borde: izquierda, derecha, arriba (maximizar), esquinas
  (cuartos). Al volver a arrastrar una encajada, recupera su tamaño.
- 1c. Movimiento propio opcional (opaco, con vista previa del encaje).
- 1d. Menú de ventana: clic central en la barra de título (y tecla): maximizar, mitades, cuartos, mosaico, al fondo,
  delante de todas, encoger, cerrar.
- 1e. Alt+Tab con lista dibujada por Trasfondo.
- 1f. Opciones en TrasfondoPrefs (sección Ventanas) y textos en los catálogos.

**Parte 2: lo que falta en Dash** (rama en `~/Projects/FreeMEMLang/.worktrees/`, los dos caminos, PR y visto bueno;
coordinar con freememlang-40)
- Observar eventos sin comérselos (filtro de commodity que no traduce a nada), con posición y momento del evento.
- La altura de la barra de título y la zona de gadgets de una ventana ajena (`wm_border`...).
- Para el explorador: permisos, comentario y fecha de un fichero (leer y poner), copiar a trozos con progreso,
  mover entre volúmenes, leer carpetas grandes de golpe (ExAll).

**Parte 3: TrasfondoArchivos** (en dos entregas)
- 3a. Ventana con lateral, migas, vista de lista y de iconos, abrir, seleccionar, copiar/mover/borrar/renombrar con
  progreso y conflictos, papelera.
- 3b. Dos paneles, arrastrar y soltar (dentro y desde el Workbench), deshacer, filtro y búsqueda, miniaturas.

## 3. Bitácora

- 2026-11-12: estudio del UX y plan. Worktree `ventanas-modernas` desde `efbb759`.
- 2026-11-12: Dash (rama `wm-eventos`): `cx_watch_add` (mirar clics sin comérselos) con `cx_event_x/y/ms`,
  `wm_box` 8-15 (bordes, zona libre de la barra, botón de cerrar), `wm_box_now`, `wm_double_click_ms`, `wm_close`.
  Arreglado: un filtro "rawmouse mouse_leftpress" nunca casaba (los botones contaban como teclas pulsadas).
- 2026-11-12: 1a, 1b y 1d escritos. Primera prueba en el emulador: el doble clic va; el encaje al soltar no. Causa:
  `wm_active` usaba `LockIBase`, que Intuition tiene cogido mientras se arrastra, así que el clic se atendía al
  soltar, con la ventana ya movida. Ahora lee bajo `Forbid`.
- 2026-11-12: textos del menú en el catálogo (300-311, con castellano). 1e: Alt+Tab y Alt+Mayús+Tab con la lista
  dibujada (la activa primero, luego de delante a detrás); al soltar Alt va a la elegida, Esc cancela.
- 2026-11-12: el encaje al soltar no saltaba porque, mientras se arrastra, Intuition no deja salir la ventana de
  la pantalla y para el puntero con ella (el puntero se queda en x=87, no llega a 0). Ahora llegar al borde es que
  la ventana quede pegada a él en ese arrastre. `tests/prueba_ventanas.py`: todo bien (encajar a la izquierda, al
  cuarto de arriba a la derecha, arriba; recuperar el tamaño; doble clic; menú con teclas, Esc y Cerrar; Alt+Tab
  y Alt+Mayús+Tab).
- 2026-11-12: capturas del menú (`tests/vista_menu.py` en 640x256 de 4 colores; `tools/vista.py --ventanas ""
  --tecla 0x40,6,25` en RTG con el tema). En pantallas de paleta usa los colores del Workbench (fondo blanco, texto
  negro, la elegida en azul); rayas entre grupos (tamaño, delante/detrás, cerrar).
- 2026-11-12: 1f: TrasfondoPrefs, página Ventanas: casillas "Encajar en los bordes", "Doble clic maximiza", "Menú de
  ventana", "Alt+Tab" (en dos columnas si caben) y la tecla del menú. Captura en RTG: bien.
- 2026-11-12: Dash (rama `wm-eventos`): `file_protection`, `file_comment`, `file_date` y sus `file_set_*`,
  `dir_entry_protection`, `dir_entry_comment`, `file_copy_attrs` y copiar a trozos (`file_copy_begin`,
  `file_copy_step`, `file_copy_end`). `tests/test_file_attrs.dash` bien por los dos caminos, A1200 y A500.
- 2026-11-12: 3a empezado: `src/archivos.dash` (TrasfondoArchivos). Decisión: ventana de MUI con una sola zona de
  dibujo (`mui_canvas`) que pinta Trasfondo con su tema; MUI da lo que una ventana propia no tendría (tamaño,
  menús con Amiga+tecla, peticiones, iconos soltados del Workbench, rueda, arrastre, teclas con calificadores).
  Hecho: lateral (sitios, discos, papelera), barra con atrás/adelante/subir y la ruta en trozos (clic en el hueco:
  escribirla), lista con columnas que ordenan, vista de iconos (los .info), elegir con Mayús y Ctrl, doble clic,
  teclado, escribir para saltar, renombrar en el sitio (sin la extensión elegida), cajón nuevo, copiar/cortar/pegar,
  arrastrar a un cajón, al lateral o a un trozo de la ruta (mismo disco mueve, otro copia, Mayús al revés), papelera
  por disco con índice para devolver, vaciarla, borrar del todo con pregunta, conflictos (reemplazar, saltar, para
  todos, cancelar), progreso abajo con cancelar (la copia a medias se borra), los .info con su fichero, avisos de
  cambios del cajón (file_notify). Textos en el catálogo (400-458) con castellano.
  `tests/prueba_archivos.py` (con el teclado, en RTG con MUI): todo bien. Capturas de lista e iconos: bien.
- 2026-11-12: dos paneles (F3; Tab cambia; F5 copia y F6 mueve al otro; lo elegido del que no manda, apagado; la
  rueda mueve el de debajo), resaltado bajo el puntero, ventana de información (Amiga+I: comentario y permisos, con
  las funciones nuevas de Dash) y deshacer (Amiga+Z: renombrar, mover, papelera; al sacar de la papelera sale del
  índice). `tests/prueba_archivos.py`: todo bien (también dos paneles, información y deshacer).
- 2026-11-12: Dash 2.11.0 y Forja 0.6.1 publicadas (aprobado por el usuario). `wm-eventos` con main fusionado
  (944779a): 626/626 sin emulador; test_wm_eventos, test_file_attrs, test_ctrl_c y test_wm bien en A1200 y A500.
- 2026-11-12: filtro (Amiga+F: solo los nombres que llevan el texto, al momento; Esc lo quita; cambiar de cajón
  también), con su píldora en la barra. Probado en `prueba_archivos.py`.
- 2026-11-12: arrastrar con el ratón probado (`GUION=prueba_arrastre.dash tests/prueba_archivos.py`): un fichero
  sobre un cajón de la lista y sobre un disco del lateral se mueve allí. Con `run_programs` y Workbench las capturas
  salen de la pantalla de arranque: para ver, `tools/vista.py`.
- 2026-11-12: buscar en los subcajones (Amiga+B): a trozos, un cajón por vuelta, sin parar la ventana; los resultados
  se ven como un cajón ("sub/fichero") y se puede copiar, mover y mandar a la papelera desde ahí (al acabar, se busca
  otra vez); Esc vuelve al cajón. Probado. `tools/paquete.py` lleva TrasfondoArchivos con su icono.
  Pendiente al publicar: `src/actualizar.dash` (el actualizador) no conoce TrasfondoArchivos (sus índices son fijos);
  miniaturas de imágenes; vista previa del encaje (1c, movimiento propio); "lista de ventanas" en la barra (es de
  Tachyon2).
- 2026-11-12: 1c: vista previa del encaje en el arrastre propio (Alt + botón izquierdo): al llegar el puntero a un
  borde sale un marco del color del acento donde quedará la ventana (cuatro ventanas finas sin borde); al alejarse se
  quita; al soltar con el marco puesto, encaja. `GUION=prueba_mover.dash tests/prueba_ventanas.py`: bien; captura
  bien. Con el arrastre de Intuition (la barra de título) sigue encajando al soltar, sin marco.
- 2026-11-12: miniaturas de imágenes (PNG, JPEG, GIF, BMP, WebP, SVG) en la vista de iconos: una a una en un
  proceso aparte (image_decode_start), reducidas a 56 x 56 sin deformar, con su marco; Ver > Miniaturas las quita.
  Captura bien; `prueba_archivos.py` bien; compila también por `--gcc`.
- 2026-11-12: `wm-eventos` con main del PR #161 (pila de rescate de las excepciones tras el StackSwap; 954584a):
  627/627 sin emulador, tests del emulador bien, pruebas de Trasfondo bien. Para las notas de 2.12 (de
  freememlang-40): "Un programa hecho con ./dash que falla con una excepción ya da el aviso, en vez de quedarse
  colgado sin sacar nada (lo destapó Tachyon en Amiberry)".
- 2026-11-12: el usuario dio el sí ("adelante"): PR #162 de Dash 2.12.0 abierto (rama wm-eventos subida); batería
  completa en marcha antes de fusionar. El actualizador (`src/actualizar.dash`) trae también TrasfondoArchivos
  (índice 11, ARCHIVOS) y lo pone en el cajón; compila, SIN probar (su prueba necesita una release en GitHub).
  Forja: el árbol de variables (idea de David Martínez) lo hace un agente en `~/Projects/forja/.worktrees/arbol`.
- 2026-11-12: PR #162 fusionado en main de Dash (f8a53d2): batería completa bien (el lote del A1200, repetido con el
  cerrojo: 911/911). Lleva también el arreglo del depurador (variables ocultas). Sin etiqueta ni release: falta el
  sí del usuario para publicar Dash 2.12.0 y Trasfondo con las ventanas y el explorador. Forja: árbol de variables
  fusionado en main local (4c71741), sin subir.
- 2026-11-12: pedido por Ferrán García (grupo, #1234-#1239): en TrasfondoArchivos, una fila de botones para las
  acciones con su tecla en el rótulo ("Copiar (F5)", "Mover (F6)", "Borrar", "Renombrar (F2)"...), sobre todo con
  dos paneles, al estilo de DOpus 4/5, DM2, RO o CLI-Mate: cada uno usa el ratón o la tecla. El usuario pide además
  ideas para que sea del todo "amiguero" (por ejemplo, los iconos de los cajones en la lista). Para la 2.9.1, con
  Ferrán en el commit, las notas y Gracias.
- 2026-11-12: Trasfondo 2.9 publicado (con Dash 2.12.1). Después, los botones de Ferrán García en TrasfondoArchivos:
  una fila abajo, cada botón con su nombre y su tecla debajo; con un panel Copiar/Cortar/Pegar (Amiga+C/X/V), con
  dos Copiar F5 y Mover F6 al otro; además Renombrar F2, Cajón nuevo, Borrar (Supr), Información y uno o dos paneles
  (F3). Apagados cuando no se pueden usar; resaltado bajo el puntero; Ver > Botones (o BOTONES=NO) la quita.
  `prueba_arrastre.dash` (clics en Copiar y Pegar) y `prueba_archivos.py` bien; capturas bien.
