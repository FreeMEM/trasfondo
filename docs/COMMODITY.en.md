# Trasfondo as a commodity

*English | [Castellano](COMMODITY.md)*

Done in Trasfondo 0.2 with Dash's `tooltype`, `cx_broker`, `cx_hotkey`, `cx_command` and `cx_wait`
builtins (PR #16). Test: `tests/prueba_commodity.py`.

Trasfondo 0.2 is controlled from Exchange, like any AmigaOS commodity. It is still written only in Dash:
whatever is missing is added to Dash as builtins, just like `desktop_canvas*` and `cpu_*`.

## What each command does

| Command | What Trasfondo does |
|---|---|
| Hide | Removes the panel from the backdrop. It keeps measuring the CPU: when you show it again, the CPU history is complete. |
| Show | Puts the panel back. |
| Disable | Removes the panel and stops measuring the CPU (`cpu_stop`). It uses nothing in the meantime. |
| Enable | Starts measuring again (`cpu_start`), with an empty history, and puts the panel back unless it was hidden. |
| Remove (Kill) | Quits and leaves the backdrop as it was. |
| Hotkey | Shows or hides the panel. It is chosen with the `CX_POPKEY` tooltype (none by default). |

Starting it again still stops it, as in 0.1 (`single_instance`). So does Ctrl-C.

Standard commodity tooltypes: `CX_PRIORITY` (broker priority), `CX_POPKEY` (hotkey) and
`CX_POPUP` (`NO`: starts hidden). From the Shell they work the same as arguments: `trasfondo CX_POPKEY="ctrl alt t"`.

## What Dash is missing

What already exists and is enough: `desktop_canvas_free` and calling `desktop_canvas` again to hide and show;
`cpu_stop` and `cpu_start` to disable and enable. We need to confirm that both pairs can be repeated
many times in the same program (create, free, create again) without leaking memory or leaving hooks installed.

Missing:

1. **Tooltypes.** Read a tooltype from the program's icon, with a default value. When started from the
   Shell, the same names as `NOMBRE=valor` arguments. This also serves phase 3 of the plan
   (position and colours through tooltypes).
2. **Commodity broker.** Register with `commodities.library` with a name, title and description (what
   Exchange shows), with the priority from `CX_PRIORITY`. It must appear only once in Exchange even if it is started
   twice (`single_instance`, which runs first, already takes care of that). It must declare that it supports showing and
   hiding (`COF_SHOW_HIDE`); otherwise, Exchange greys out those two buttons.
3. **Hotkey.** Set up a hotkey from its description (`"ctrl alt t"`). If the description
   isn't valid, say so (so it can be reported in the output) instead of failing.
4. **Receiving commands.** A function that says which command arrived: none, hide, show, disable,
   enable, remove or hotkey. On disable and enable, the broker must change its own state
   (`ActivateCxObj`), so that Exchange shows it correctly and the hotkey doesn't work while it is
   disabled.
5. **Waiting without using CPU.** Right now the loop sleeps for a second (`time_delay(50)`) and then checks `break_check`.
   We need a wait that ends when the time runs out, when a command arrives from Exchange or when Ctrl-C arrives,
   whichever happens first. That way the command is carried out straight away and not on the next second.
6. **On exit**, the broker and the hotkey are removed automatically, as `desktop_canvas_free` does with the backdrop.

The names and shape of the functions are up to Dash, in its own style.

## How to test it

In the emulator (AmigaOS 3.2.3 and RTG), with Exchange open:

- Trasfondo appears in the list with its title and description.
- Hide and Show ten times in a row: the panel goes away and comes back, the icons stay intact and free
  memory doesn't go down.
- Disable: the panel goes away and Trasfondo's CPU drops to 0. Enable: it comes back with an empty history.
- The hotkey hides and shows; when disabled, it does nothing.
- Remove, starting it again and Ctrl-C: it quits, the backdrop is left as it was and it no longer appears in Exchange.
- With `CX_POPUP=NO` it starts hidden.
