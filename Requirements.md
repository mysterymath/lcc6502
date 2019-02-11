# Requirements

The C standard, the nature of the 6502, and the nature of each target
platform each impose a number of requirements for the design of a suitable
compiler. These requirements are gathered here, organized by topic.

* The system must be ANSI C compliant for a freestanding implementation.

* In concert with an assembler, the compiler must be capable of producing a
  program that boots from the following kinds of Atari ROM cartridge:
  * 8KB
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

* The compiler must provide a means for the user to specify what address
    regions (including Zero Page) are available for use by the compiler. This
    must include which address regions are RAM or ROM and the number of banks
    available at various address regions. The compiler must produce code and
    data that resides in those address regions, such that the code produced
    can be included into an assembly program that describes the full program.

* The compiler must produce code that runs correctly on either a NMOS or CMOS
    6502.

* It must be possible to call C routines from assembly language, including from
    interrupt handler routines.

* It must be possible to include inline assembly language routines in C
    functions.

    * It must be possible to specify that the values of certain input
        expressions be placed in certain registers or flags.

    * It must be possible to specify that output values in certain registers or     flags be assigned to C objects.

    * It must be possible to specify that certain registers or flags have been
        overwritten with undefined values by the routine (clobbered).

    * The S register and the C stack pointer (if any) must both have the same       value after the routine as before.

* The register save and restore overhead for every call, even those crossing a
  C/assembly boundary, must be small and finite. This is particularly true when calling a C function from an interrupt handler.

* No optimizations may be performed that would cause a program to no longer fit
    into available RAM/ROM.

* The implementation must define <setjmp.h> suitable for a hosted
    implementation of ANSI C, though only a freestanding implementation is
    provided.

* The number of registers saved by `setjmp` and restored by `longjmp` must be
    tightly bounded.

* `longjmp` should restore the interrupt disable flag, since it may be used to
    escape from an interrupt.