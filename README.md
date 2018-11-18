# LCC 6502 C Compiler
This project is to create a modern C compiler for the MOS 6502. When finished,
it will allow writing performance-sensitive projects for the Atari 800 (and
eventually other 6502 platforms) entirely in C, without any hand-written
assembly.

# Project Status
This project is gathering requirements, and nothing useful has been designed or
implemented yet. Check back later for updates.

Updated November 15, 2018.

# Planned Features
* ANSI C Compatibility. For each supported target, the project must meet the
  requirements for a hosted implementation set forth in the latest
[freely-availible draft](http://port70.net/~nsz/c/c89/c89-draft.html) of ANSI
X3.159-1989 "Programming Language C."
  * C standard compatibility allows running as many libraries as possible
    without modification. Modification may still be required for either
non-portable or insufficiently performant libraries.
  * ANSI C was the C standard from 1989 to 1999, and is largely
    backwards-compatible with the previous C implementation. Many C libraries
are written against it.
  * The project must supply hosted implementations of the language (see the C
    standard). This allows programs to be written that feel more like writing
on a personal computer, and less like writing on a microcontroller. These
platforms largely do have operating systems already, and these OS routines can
be leveraged to create native hosted implementations.
  * The next version of the C standard, C99, requires that hosted
    implementations support "65535 bytes in an object." This precludes creating
a hosted implementation for C99 on the 6502, which can address at most 65536
bytes. Such an object would take up the entire addressible memory space.
  * The draft is used since the production standard is "generally known" not to
    differ from the draft, and the production standard is difficult to obtain.
No technical corrigenda need be considered, since these were not availible at
the time of drafting.
* Atari 800 target. The compiler must produce output capable of running on an
  Atari 800.
* C64 target. The computer must produce output capable of running on the
  Commodore 64.
* Fast code. The output produced by the compiler should be within an order of
  magnitude as fast as that written by a human transliterating the C to
equivalent assembly. Most high-level optimzations are left to the C author.
  * Whenever possible, the compiler must perform 8-bit arithmetic operations
    directly, instead of integral promotions.

# Project Design
The project is currently gathering requirements; design is TBD.

To understand the problem space and potential solution techniques, start with
David A. Wheeler's excellent [guide](https://dwheeler.com/6502/).

The LCC compiler has been chosen as a C frontend for its simplicity, ANSI C
standards compliance, and excellent documentation. It's backend interface
[documentation](http://storage.webhop.net/documents/interface4.pdf) is freely
available.  The relevant parts of the compiler are in the [lcc/](lcc/)
subdirectory.

Design implications from the ANSI C standard:

1 [INTRODUCTION](http://port70.net/~nsz/c/c89/c89-draft.html#1.)
  - All implementation-defined behaviors or characteristics in the standard need to be explicitly defined.
  - All extensions to the standard need to be defined.
  - No extensions are allowed that would render a strictly conforming program nonconforming.

4.10.4.5 [The system function](http://port70.net/~nsz/c/c89/c89-draft.html#4.10.4.5)
  - The system function must always return zero, since no command processor is
    available. 
  
        

# For More Details
## Prototype ([prototype/](prototype/))
A basic proof-of-concept prototype for the compiler. 

## LCC ([lcc/](lcc/))
The relevant parts of the LCC compiler. Currently just the C preprocessor and C
compiler proper. All other backends except "bytecode" have been removed.

# Why?
The 6502 is hardly dead; there is still quite an active hobbyist community for
the chip. It was used in the Atari 8-bit, the Apple II, and the NES, amongst
others, so it's wormed its way into quite a few hearts, including the author's.
It's also worming its way into consumer products: it continues to be produced
today and sold in bulk.  The techniques used in the construction of this
project may also be useful for other similar platforms.

# Why not X?
## Why not CC65?
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
this property. As a result, even though most of the project can be written in
C, all inner loops stil need to be written in assembly.  Instead, a C compiler
should allow writing a full project end-to-end in C, even the parts that need
to be (reasonably) fast.

## Why not [PLASMA](https://github.com/dschmenk/PLASMA)/[Atalan](http://atalan.kutululu.org/)/[Forth](https://en.wikipedia.org/wiki/Forth_(programming_language))/etc.?
These aren't C. C is a nice language that everyone and their mother knows;
these languages are a bit more on the esoteric side of the tracks.

## Why not compile to PLASMA?
A C compiler is expected to produce native machine code, suitable for tight
interrupt handlers and real-time routines.  When writing these in C, one loses
the cycle-per-cycle control of the CPU one has in assembly, but one gains ease
of use and super-human efficiency in register and memory allocation. Compiling
to a virtual machine like PLASMA would prevent writing such routines in C,
since the indirection cost would be too high.

