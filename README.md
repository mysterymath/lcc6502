# LCC 6502 C Compiler

This project is to create a modern C compiler for the MOS 6502. When finished,
it will allow writing performance-sensitive projects for the Atari 800 (and
eventually other 6502 platforms) entirely in C, without any hand-written
assembly.

## Project Status

This project is gathering requirements, and nothing useful has been designed or
implemented yet. Check back later for updates.

Updated November 15, 2018.

## Planned Features

* [C89 Compatibility](C_Standard_Compliance.md). For each supported target, the
  project must meet the requirements for a hosted implementation set forth in
  the latest [freely-availible
  draft](http://port70.net/~nsz/c/c89/c89-draft.html) of ANSI X3.159-1989
  "Programming Language C."
* Atari 800 target. The compiler must produce output capable of running on an
  Atari 800.
* C64 target. The computer must produce output capable of running on the
  Commodore 64.
* Fast code. The output produced by the compiler should be within an order of
  magnitude as fast as that written by a human transliterating the C to
  equivalent assembly. Most high-level optimzations are left to the C author.
  * Whenever possible, the compiler must perform 8-bit arithmetic operations
    directly, instead of integral promotions.

## Project Design

The project is currently gathering requirements; design is TBD.

To understand the problem space and potential solution techniques, start with
David A. Wheeler's excellent [guide](https://dwheeler.com/6502/).

The LCC compiler has been chosen as a C frontend for its simplicity, standards
compliance, and excellent documentation. It's backend interface
[documentation](http://storage.webhop.net/documents/interface4.pdf) is freely
available.  The relevant parts of the compiler are in the [lcc/](lcc/)
subdirectory.

### Design implications from the C89 standard

1 [INTRODUCTION](http://port70.net/~nsz/c/c89/c89-draft.html#1.)

* All implementation-defined behaviors or characteristics in the standard need
  to be explicitly defined.
* All extensions to the standard need to be defined.
* No extensions are allowed that would render a strictly conforming program
  nonconforming.

TODO: Sections 2+ of the standard.

### Implementation-Defined Behavior

1.6 [DEFINITIONS OF TERMS](http://port70.net/~nsz/c/c89/c89-draft.html#1.)

* A byte contains 8 bits.
* TODO: The number, order, and encoding of each byte in an object, except where
  expliclitly defined by the C spec.

4.10.4.5 [The system
function](http://port70.net/~nsz/c/c89/c89-draft.html#4.10.4.5)

* The system function must always return zero, since no command processor is
  available.

TODO: Sections 2+ of the standard.

## For More Details

### Prototype ([prototype/](prototype/))

A basic proof-of-concept prototype for the compiler. 

### LCC ([lcc/](lcc/))

The relevant parts of the LCC compiler. Currently just the C preprocessor and C
compiler proper. All other backends except "bytecode" have been removed.

## Other Approaches

### CC65

Word around the Internet is that CC65 (an existing C compiler) produces output
that is much slower than human-written assembly.  For example, blogger XtoF
[attempted](https://www.xtof.info/blog/?p=714) to use CC65 to write a simple
game of life implementation for the Apple II. While the compiler produced
correct code and was easy to use, the [results](https://youtu.be/1twMsK6wXgg)
were too slow to be practical.  Examining the output revealed that the inner
loop of the simulation, a tight 7 line C routine, had been transformed to over
200 instructions, including many subroutine calls. A hand-written assembly
routine, exactly following the C instructions, would have been only a dozen or
so instructions.

Modern C compilers provide an essential fiction: the system appears to natively
run C. While it's usually quite trivial for an assembly author to beat a C
compiler (especially on as simple a CPU as the 6502), it's usually not
worthwhile to do so, since the gains are usually minor.  CC65 broadly violates
this property. As a result, even though most of the project can be written in C,
all inner loops stil need to be written in assembly.  Instead, a C compiler
should allow writing a full project end-to-end in C, even the parts that need to
be (reasonably) fast.

### Why not [PLASMA](https://github.com/dschmenk/PLASMA)/[Atalan](http://atalan.kutululu.org/)/[Forth](https://en.wikipedia.org/wiki/Forth_(programming_language))/etc.?

These aren't C. C is a nice language that everyone and their mother knows; these
languages are a bit more on the esoteric side of the tracks.

### Compile to PLASMA

A C compiler is expected to produce native machine code, suitable for tight
interrupt handlers and real-time routines.  When writing these in C, one loses
the cycle-per-cycle control of the CPU one has in assembly, but one gains ease
of use and super-human efficiency in register and memory allocation. Compiling
to a virtual machine like PLASMA would prevent writing such routines in C, since
the indirection cost would be too high.