# Requirements

The C standard, the nature of the 6502, and the nature of each target
platform each impose a number of requirements for the design of a suitable
compiler. These requirements are gathered here, organized by topic.

## C Language

* For each supported target, the compiler must conform to the requirements for
    a freestanding implementation of ANSI C, as laid out in the latest
    freely-available draft, including all technical corrigenda.
    
    * To ensure this, a suite of automated tests must be written to test each
        aspect of the standard.

* It must be possible to extend the compiler to hosted implementation of C by
    writing C libraries.

* When there's no compelling reason to do otherwise, the C should be like that
    inside a POSIX environment.

## C/Assembly Interoperability

* It must be possible to call C routines from assembly language, including from
    interrupt handler routines.

    * To ensure this, an automated test must be written that calles a C
        function from an Atari 800 interrupt handler.

* It must be possible to call assembly language routines from C.

    * To ensure this, an automated test must be written that calls an
        assembly-language routine from C.
        

## Execution Environments

* The compiler must support at least the Atari 800 and the Commodore 64.

* In concert with an assembler, the compiler must be capable of producing a
  program that boots from an OSS one-chip 16 KB cartridge (Atari800 type 15).

    * To ensure this, an automated test must be written for each.

* In concert with an assembler, the compiler must be capable of producing a
    program that boots from an Atari 800 cassette.

    * To ensure this, an automated test must be written.

* In concert with an assembler, the compiler must be capable of producing a
    program that boots from an Atari 800 diskette.

    * To ensure this, an automated test must be written.

* In concert with an assembler, the compiler must be capable of producing a
    program that can be run from Atari DOS 2.5.

    * To ensure this, an automated test must be written.

* In concert with an assembler, the compiler must be capable of producing a
    function that can be called using the Atari BASIC `USR` statement.

    * To ensure this, an automated test must be written.

* In concert with an assembler, the compiler must be capable of producing a
    program that `RUN`s when `LOAD`ed from a Commodore 64 disk.

    * To ensure this, an automated test must be written.

* In concert with an assembler, the compiler must be capable of producing a
    program that boots from a Commodore 64 cartridge.

    * To ensure this, an automated test must be written.

* The compiler must produce code that runs correctly on either a NMOS or CMOS
    6502.

    * To ensure this, automated tests must be written for each known difference
        between the NMOS and CMOS chips.

## Performance

* The output produced by the compiler should be roughly as fast as that written
    by a human transliterating the C to equivalent assembly.

    * To ensure this, automated tests must be written for scenarios that are
        determined to be difficult to efficiently compile. These scenarios
        and tests should be written throughout implementation.

* No optimizations may be performed that would cause a program to no longer fit
    into available RAM/ROM.

    * To ensure this, an automated test must be written for a program near the
        size limit on an Atari 800.
