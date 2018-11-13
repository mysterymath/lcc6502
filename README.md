# LCC 6502 C Compiler
This project is to create a modern C compiler for the MOS 6502. When finished,
it can build performance-sensitive projects for the Atari 800 (and eventually
other 6502 platforms) entirely in C, without any hand-written assembly.

# Project Status
This project is still under design, and nothing useful has been implemented
yet. Check back later for updates.

Updated November 12, 2018.

# Why?
I first learned to program on the Atari 800, and it will always have a very
special place in my heart. I've long wanted to make a some fun hobby projects
for the old 800, but I've hesitated, since I know I'd quickly find myself
missing the niceties of modern software development. Python is probably too
much to ask for, but a proper C compiler doesn't seem doesn't that
unreasonable.  
The zeitgeist seems to be that writing a proper C compiler for this CPU (the
MOS 6502) is difficult to the point of impossibility. Upon hearing this, I knew
that I immediately had to make an attempt. In a way, I feel a bit like a
mathematician hearing about Fermat's last theorem; armed with my amateur
postulates, I will not believe it is that difficult until I've at least tried
it.

That covers the personal reasons; now for the practical. The 6502 is hardly
dead; there is still quite an active hobbyist community for the chip. It was
used in the Atari 8-bit, the Apple II, and the NES, amongst others, so it's
wormed its way into quite a few hearts, not just mine. It's also worming its
way into consumer products: it continues to be produced today and sold in bulk.
The techniques used in the construction of this project may also be useful for
other similar platforms, though portability is not a goal.

# Why not X?
## Why not CC65?
Vague consensus on the Internet seems to be that CC65 (the existing C compiler)
produces quite slow machine code, very dissimilar human-written assembly.  For
example, blogger XtoF [attempted](https://www.xtof.info/blog/?p=714) to use
CC65 to write a simple game of life implementation for the Apple II. While the
compiler produced correct code and was easy to use, the
[results](https://youtu.be/1twMsK6wXgg) were too slow to be practical.
Examining the output revealed that the inner loop of the simulation, a tight 7
line C routine, had been transformed to over 200 instructions, including many
subroutine calls. A hand-written assembly routine, exactly following the C
instructions, would have been far shorter and far faster.

Modern C compilers provide an essential fiction to the user: the system appears
to natively run C. While it's usually quite trivial to beat a C compiler
(especially on as simple a CPU as the 6502), it's usually not worthwhile to do
so, since the gains are minor.  CC65 broadly violates this property. As a
result, even though most of the project can be written in C, all inner loops
stil need to be written in assembly.  Instead, this compiler should allow
writing a full project end-to-end in C, even the parts that need to be
(reasonably) fast.

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

# Project Requirements
- C89 Compatibility.
  - The project should meet the requirements set forth in ANSI X3.159-1989 "Programming Language C."
  - The project need only supply a freestanding implementation. A hosted implementation may someday be written.
- Fast code.
  - The output produced by the compiler should be within an order of magnitude as fast as that written by a human.
- Many more to come.

## Explicit Non-Requirements
- High-level optimizations.
  - The output assembly should roughly follow the outline set by the C source.
    Optimizations like loop unrolling and induction variable optimizations are
left to the programmer. This gives more precise control of the output assembly
to the programmer, albeit filtered through C.
- Portability.
  - The techniques may transfer to other similar architectures, but trying to
    keep things open for other architectures will make an already difficult
task moreso, and would likely still result in something insufficiently
portable.  

# Project Design
A good starting point is David A. Wheeler's excellent [guide](https://dwheeler.com/6502/).

More to come in this section. I know a lot, but I still have to write it down
and properly attribute all the ideas that aren't mine (most of them, really).

The LCC compiler has been chosen as a frontend for its simplicity and excellent
documentation. It's backend interface [documentation](http://storage.webhop.net/documents/interface4.pdf) is freely available.
The relevant parts of the compiler are in the [lcc/](lcc/) subdirectory.

# Project Layout
## Prototype ([prototype/](prototype/))
A basic proof-of-concept prototype for the compiler. 

## LCC ([lcc/](lcc/))
The relevant parts of the LCC compiler. Currently just the C preprocessor and C
compiler proper. All other backends except "bytecode" have been removed.
