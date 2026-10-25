# Disks, network and WiFi

*English | [Castellano](DISCOS_Y_RED.md)*

Done in Trasfondo 0.2 with Dash's `disks_*`, `net_if*` and `wifi_*` builtins (PR #17). Disks tested in the
emulator; network and WiFi not yet tested with Roadshow or with real WiFi.

Three new panels for Trasfondo, requested by users coming from NewMeter:

- **Disks**: each mounted volume, with its capacity and how full it is.
- **Network**: what comes in and goes out per second.
- **WiFi**: the signal quality, and whether the network is connected or not.

Like the rest, in pure Dash: whatever is missing is added to Dash as builtins.

## What to avoid (NewMeter's failings)

- **Hanging the system** when querying the WiFi. No query may wait indefinitely: if the
  device doesn't answer within a short time (half a second, for example), that read is abandoned
  (`AbortIO`) and the panel says so ("no response").
- **Not noticing that the network was disconnected.** Every read is done afresh, without trusting data or
  devices opened earlier. If the interface disappears or the device is closed, the panel says so, and
  shows data again when the network comes back. Without having to quit Trasfondo.
- **See-through window with leftovers from other windows.** Trasfondo doesn't have that problem: it paints on the real
  backdrop, not in a window.

## Disks

For each mounted volume with a disk inserted: name, total size, used and free (`Info()` on the
volume). Without asking "Please insert volume" (`dos_requesters(false)` already exists) and without getting stuck waiting for
a slow or network volume: if it doesn't answer, it is skipped.

Missing builtins: the list of mounted volumes and, for each one, its size and free space.

## Network

Bytes received and sent on each interface, to work out the speed by subtracting one read from the previous one.
With Roadshow, `ObtainInterfaceList` and `QueryInterfaceTagList` from `bsdsocket.library` give the interfaces,
their state and their byte counters. With other stacks (AmiTCP, Miami) that don't have it, the panel doesn't appear.

Missing builtins: the list of interfaces, their state (connected or not) and their incoming and outgoing bytes.

## WiFi

The signal quality is requested from the interface's SANA-II driver (its name and unit, from Roadshow) with the
signal quality command of the SANA-II wireless extension (the one provided by `prism2.device` and other
drivers by Neil Cafferkey: signal and noise level). If the driver doesn't have it, the panel shows only
connected or disconnected.

Missing builtin: the signal quality of an interface, with a maximum wait time.

The exact names of tags and commands need to be checked in the Roadshow and SANA-II includes.

## How to test it

- Disks: in the emulator, with several volumes (DH0, RAM, a floppy disk and the empty floppy drive). The
  numbers must match those of `Info` in the Shell, and the empty drive must not ask for a disk.
- Network: in the emulator with networking and Roadshow, downloading a file: the speed must match that of the
  download. Without Roadshow, the panel doesn't appear and nothing fails.
- Disconnecting the network while running (in the emulator, removing the interface with `NetShutdown`, or taking it down): the panel
  says so straight away, nothing hangs, and when the network comes back it gives data again.
- WiFi: the emulator has no WiFi. It has to be tested on a real Amiga with a WiFi card (`prism2.device`).
