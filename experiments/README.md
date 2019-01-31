# Experiments

This directory contains experiments run on target hardware to determine their requirements.

## cart_brk

`crt_brk.rom` is an 8KB Atari 800 cartridge that places BRK instructions in
both the init and start addresses. It allows determining whether init is run in
various configurations.

In particular, Atari DOS 2.5 does not run the init routine when option `B. Run
Cartridge` is selected. It also does not JSR to the init routine, unlike the
Atari OS; a JMP is used instead.
