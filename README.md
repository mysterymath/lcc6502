# LCC 6502 C Compiler

This project is to create a modern C compiler for the MOS 6502. When finished,
it will allow writing performance-sensitive projects for the Atari 800 (and
eventually other 6502 platforms) entirely in C, without any hand-written
assembly.

## Project Status

This project is gathering requirements, and nothing useful has been designed or
implemented yet. Check back later for updates.

Updated December 30, 2018.

## Requirements

[Requirements](Requirements.md) have been collected by analyzing the ANSI C
standard, the programming manuals for the Atari 800 and the Commodore 64, and
the NMOS and CMOS 6502 instruction set and quirks.

## Project Design

The project is currently under [design](Design.md).

To understand the problem space and potential solution techniques, start with
David A. Wheeler's excellent [guide](https://dwheeler.com/6502/).

The LCC compiler has been chosen as a C frontend for its simplicity, standards
compliance, and excellent documentation. It's backend interface
[documentation](http://storage.webhop.net/documents/interface4.pdf) is freely
available.  The relevant parts of the compiler are in the [lcc/](lcc/)
subdirectory.

### Work Items

* [ ] Develop OSS one-chip 16KB Atari 800 ROM cartridge acceptance test.
* [ ] Develop 8KB Atari 800 ROM cartridge acceptance test.
* [ ] Develop Assembly to C acceptance test.
* [ ] Develop Atari 800 diskette bootloader acceptance test.
* [ ] Develop Atari 800 cassette acceptance test.
* [ ] Develop Commodore cartridge acceptance test.
* [ ] Develop Commodore disk `LOAD` acceptance test.
* [ ] Develop Atari 800 diskette acceptance test.
* [ ] Develop Atari 800 DOS 2.5 load acceptance test.
* [ ] Develop all necesary NMOS vs CMOS acceptance tests.
* [ ] Develop C to assembly acceptance test.
* [ ] Develop C standard acceptance tests.
* [ ] Organize known design considerations (knowns).
* [ ] Collect design questions (unknowns) to be answered by design spikes.

## For More Details

### [Requirements](Requirements.md)

The C standard, the nature of the processor, and the nature of each target
platform each place specific requirements on the implementation. Any
non-trivial requirements are collected here.

### [Implementation-Defined Behavior](Implementation_Defined_Behavior.md)

The C89 standard requires a conforming implementation to document a number of
"implementation-defined" behaviors and characteristics. All such definitions
can be found at the link above.

### [Design](Design.md)

This will be a broad overview of the design of the compiler. WIP.

### Prototype ([prototype/](prototype/))

A basic proof-of-concept prototype for the compiler.

### LCC ([lcc/](lcc/))

The relevant parts of the LCC compiler. Currently just the C preprocessor and C
compiler proper. All other backends except "bytecode" have been removed.

### Other Resources

For a very detailed description of the behavior of the 6510 processor (the
variation of the 6502 used in the Commodore 64), see
[64doc.txt](http://www.atarihq.com/danb/files/64doc.txt). The 6510's instuction
set and behavior is essentially the same as the 6502 for the purposes of this
compiler.

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
