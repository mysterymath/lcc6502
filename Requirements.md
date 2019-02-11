# Requirements

The C standard, the nature of the 6502, and the nature of each target
platform each impose a number of requirements for the design of a suitable
compiler. These requirements are gathered here, organized by topic.

## C Language

* For each supported target, the compiler must conform to the requirements for
    a freestanding implementation of ANSI C, as laid out in the latest
    freely-available draft, including all technical corrigenda.

* It must be possible to extend the compiler to hosted implementation of C by
    writing C libraries.

* When there's no compelling reason to do otherwise, the C should be like that
    inside a POSIX environment.

## C/Assembly Interoperability

* It must be possible to call C routines from assembly language, including from
    interrupt handler routines.

* It must be possible to call assembly language routines from C.

## Execution Environments

* The compiler must support at least the Atari 800 and the Commodore 64.

* In concert with an assembler, the compiler must be capable of producing a
  program that boots from the following kinds of Atari ROM cartridge:
  * Standard 8KB
  * OSS one-chip 16 KB cartridge (Atari800 type 15)

* In concert with an assembler, the compiler must be capable of producing a
    program that boots from an Atari 800 cassette.

* In concert with an assembler, the compiler must be capable of producing a
    program that boots from an Atari 800 diskette.

* In concert with an assembler, the compiler must be capable of producing a
    program that minimally boots from an Atari 800 diskette, loads the rest of
    itself, then runs the code that it loaded.

* In concert with an assembler, the compiler must be capable of producing a
    program that can be run from Atari DOS 2.5.

* In concert with an assembler, the compiler must be capable of producing a
    program that returns control to Atari DOS 2.5 after being loaded.

* In concert with an assembler, the compiler must be capable of producing a
    function that can be called using the Atari BASIC `USR` statement.

* In concert with an assembler, the compiler must be capable of producing a
    program that `RUN`s when `LOAD`ed from a Commodore 64 disk.

* In concert with an assembler, the compiler must be capable of producing a
    program that boots from a Commodore 64 cartridge.

* The compiler must produce code that runs correctly on either a NMOS or CMOS
    6502.

## Performance

* The output produced by the compiler should be roughly as fast as that written
    by a human transliterating the C to equivalent assembly.

* No optimizations may be performed that would cause a program to no longer fit
    into available RAM/ROM.