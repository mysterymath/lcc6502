# LCC 6502 C Compiler

This project is to create a modern C compiler for the MOS 6502. When finished,
it will allow writing performance-sensitive projects for the Atari 800 (and
eventually other 6502 platforms) entirely in C, without any hand-written
assembly.

## Project Status

This project is gathering requirements, and nothing useful has been designed or
implemented yet. Check back later for updates.

Updated November 25, 2018.

## Planned Features

* [C89 Compatibility](C_Standard_Compliance.md). For each supported target, the
  project must meet the requirements for a freestanding implementation set forth
  in the latest [freely-availible
  draft](http://port70.net/~nsz/c/c89/c89-draft.html) of ANSI X3.159-1989
  "Programming Language C."
* Atari 800 target. The compiler must produce output capable of running on an
  Atari 800.
* C64 target. The compiler must produce output capable of running on the
  Commodore 64.
* ROM-compatible. The compiler must produce output capable of running from ROM.
* POSIX-ish-ness. When there's no compelling reason to do otherwise, the C
  should be like that inside a POSIX environment.
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

1.7 [COMPLIANCE](http://port70.net/~nsz/c/c89/c89-draft.html#1.7.)

* Freestanding implementations must implement all library features found in:
  * float.h
  * limits.h
  * stdarg.h
  * stddef.h

* All implementation-defined behaviors or characteristics in the standard need
  to be explicitly defined.
* All extensions to the standard need to be defined.
* No extensions are allowed that would render a strictly conforming program
  nonconforming.

2 [ENVIRONMENT](https://port70.net/~nsz/c/c89/c89-draft.html#2.)

2.1 [CONCEPTUAL MODELS](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.)

2.1.1 [Translation
environment](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.1.)

2.1.1.1 [Program structure](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.1.)

* While it's not necessary to perform traditional separate compilation (i.e.,
  changing one .c file only requires recompiling that one file), much of the C
  universe is designed assuming this is the case. This implementation should
  support it as far as is possible without hindering performance.

2.1.1.3 [Diagnostics](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.1.3.)

* TODO: Determine whether there are any syntax rule or constraint violations
  that can only be detected by the backend. The backend will need to produce
  diagnostic messages for these, if any.

2.1.2 [Execution
environments](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.2.)

* Objects in static storage need to be initialized *before* program startup. For
  ROM output, this means that mutable static objects need to be copied to RAM
  locations. These would become the canonical locations for the objects.

2.1.2.1 [Freestanding
environment](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.2.1.)

* At program startup, the routine with the name "_start" is called. This
  function must take no arguments and have a void return type.

2.1.2.3 [Program execution](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.2.3.)

* Reads from volatile objects need to be treated differently, so that information needs to
  be extacted from LCC.
* Automatic variables need to retain their values across signal handling
  suspensions. This implies either keeping them in no-clobber registers or
  saving them on a stack.

2.2.1 [Character sets](https://port70.net/~nsz/c/c89/c89-draft.html#2.2.1)

* Neither  their Atari 800 (ATASCII) or Commodore 64 (PETSCII) character sets
  contain '{' or '}', which are both required by the standard for both source
  and execution environments.
* At least one target character set, ATASCII, does not contain a null character
  at zero. This means it cannot simply support null-terminated strings.
* Neither of the character ROM encodings for ATASCII and PETSCII have a null
  character at zero.
* String literals need not be strings (they can contain '\0' anywhere within),
  but the standard requires their value ends in a null character.
* The implementation should provide C-style null-terminated string literals,
  since there's no other way to achieve C89 compatibility.
* The implementation should also provide macros that wrap string literals. These
  allow producing non-null-terminated strings, which can include null-valued
  characters in strings, which are meaningful in some target character sets.
  * For example:
    * _ATASCII("\0") would produce a heart in ATASCII.
    * _ATASCII("Hello") would produce "Hello" in ATASCII, not null-terminated.
    * _ANTIC("Hello") would produce "Hello" in ANTIC display codes, not null-terminated.
    * _PETSCII_U("HELLO") would produce "HELLO" in unshifted PETSCII, not null-terminated.
    * _PETSCII_S("Hello") would produce "Hello" in shifted PETSCII, not null-terminated.
    * Given `const char kHello[] = "Hello";`, the value of `sizeof(kHello)` is 6.
    * Given `const char kHello[] = _ATASCII("Hello");`, the value of `sizeof(kHello)` is 5.
    * _PETSCII_U("Hello") would produce a compile error, since lowercase letters
      are unmapped in unshifed PETSCII.
  * The implementation should provide a way to define such macros and their
    corresponding ASCII->execution character set mappings.
  * No mechanism is provided to change the default interpretation of character
    literals, since such literals would no longer work with routines designed
    for C strings. This behavior is sufficiently dangerous to require explicit
    denotation in the source text.

2.2.2 [Character display semantics](https://port70.net/~nsz/c/c89/c89-draft.html#2.2.2)

* Escape characters should not output a printable character.
* Alert must not change the cursor position.
* Carriage return should move the cursor to the initial position of the current line.

2.2.3 [Signals and interrupts](https://port70.net/~nsz/c/c89/c89-draft.html#2.2.3)

* No signals need be provided, but to allow implementing signals, intterupt
  handlers must be writable in pure C.
  * A function should be markable as an interrupt handler. TODO: Define syntax
    and semantics.
  * It must be possible to enable and disable interrupts. TODO: Define syntax
    and semantics.
  * Any function can be interrupted at any time by an interrupt, which can call
    any C function.
    * Interrupt handlers must not overrite any locations (memory or register)
      used by previous invocations or by any active functions.
    * Interrupt handlers often need to be extremely timely, so the number of
      locations saved and restored by the handler must be tightly bounded.

2.2.4.1 [Translation limits](https://port70.net/~nsz/c/c89/c89-draft.html#2.2.4.1)

* A hosted implementation cannot be constructed for target platforms, since
  neither the Atari 800 nor the C64 have 32767 bytes of contiguous RAM. ROM
  doesn't help either; the max amount typically used is too small.
* Each function needs to support at least 31 arguments. That's at least 31 bytes
  of storage.
* At least 257 case labels need to be supported. This precludes creating a sort
  of byte-indexed perfect-hashed jump table, since there would be too many
  entries in the worst case. This is to allow branching on any character as well
  as EOF.
* This implementation should avoid any unneccesary limits. For sizes, that means
  that a program should only be rejected if it cannot be made to fit in the
  available resources on the target system.
  * No optimizations (inlining, etc) may be performed unless it can be
    guaranteed that it will not cause a fitting program to no longer fit.
  * If a program cannot be made to fit, the compiler should turn parts of the
    program into compact, slower code, starting with the parts with least
    performance impact. The program should not be rejected until the compiler
    has replaced all of it with compact code.
  * The compiler should aim for the most efficient program that can be made to
    fit.

2.2.4.2 [Numerical limits](https://port70.net/~nsz/c/c89/c89-draft.html#2.2.4.2)

* Sign extending chars is expensive on the 6502, and at least one major POSIX
  platform (ARM) does not sign extend chars. Thus, the implementation, like ARM,
  defines CHAR_MIN to be 0 and CHAR_MAX to be the same as UCHAR_MAX.

3.1.2.1 [Scopes of identifiers](https://port70.net/~nsz/c/c89/c89-draft.html#3.1.2.1)

* The backend needs to obtain scoping information from LCC, so that otherwise
  identical identifiers with different scope in LCC's output do not conflict
  with one another.

* "{ extern int f(); }" has block scope, even though it refers to an external
  function. TODO: Determine LCC's behavior in this case.

* Prototypes in library headers may only use identifiers in the reserved
  namespace (__x or _X). Otherwise, the user could place a #define macro before
  the header as follows:
  ```C
    #define status []
    void exit(int status);
  ```

  This becomes:

  ```C
    void exit(int []);
  ```

3.1.2.4 [Storage duration of objects](https://port70.net/~nsz/c/c89/c89-draft.html#3.1.2.4)

* Automatic objects that can be proven never to be present in two
  simultaneously active invocations can be treated much like static objects.
  * If the objects were initialized, the initialization still needs to happen
    each time, unlike statics, which are initialized before program startup.
  * Values of pointers to auto objects in terminated blocks are indeterminate.
    This means that objects in blocks that cannot be simultaneously active can
    have the same pointer value.
  * It's simplest to only bump the stack pointer once at the beginning of a
    function. Otherwise, any goto statements that enter a block need to
    allocate all the space required for that block.

TODO: Section 3.1.2.6+

### Implementation-Defined Behavior

1.6 [DEFINITIONS OF TERMS](http://port70.net/~nsz/c/c89/c89-draft.html#1.)

* A byte contains 8 bits.
* TODO: The number, order, and encoding of each byte in an object, except where
  expliclitly defined by the C spec.

2.1.2.1 [Freestanding
environment](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.2.1.)

* TODO: Define the library routines provided by this implementation.
* All external identifiers that begin with an underscore are reserved. All other
  identifiers that begin with an underscore and either an upper-case letter or
  another underscore are reserved. If the program defines an external identifier
  with the same name as a reserved external identifier, even in a semantically
  equivalent form, the behavior is undefined.

2.1.2.3 [Program execution](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.2.3.)

* This implementation defines no interactive devices.

2.2.1 [Character sets](https://port70.net/~nsz/c/c89/c89-draft.html#2.2.1)

* The source character set is ASCII for all targets.
* For the Atari 800 the execution character set is ATASCII.
  * ASCII '{' is mapped to inverse '['.
  * ASCII '}' is mapped to inverse ']'.
  * ASCII '~' is mapped to inverse '-'.
  * ASCII vertical tab is mapped (somewhat arbitrarily) to "Cursor Down".
  * ASCII form feed is mapped to "Clear Screen".
  * ASCII alert is mapped to "Buzzer".
  * ASCII carriage return is mapped (somewhat arbitrarily) to "Cursor Left".
  * All other members of the basic character set take their natural mappings.
  * An alternative mapping is provided for the internal ROM character mapping.
* For the Commodore 64 the execution character set is PETSCII.
  * ASCII '^' is mapped to up arrow.
  * ASCII '\' is mapped to the British pound sign.
  * ASCII '|' is mapped to $DD.
  * ASCII '~' is mapped to $B2.
  * ASCII '{' is mapped to $EB.
  * ASCII '}' is mapped to $F3.
  * ASCII tab is mapped (somewhat arbitrarily) to "Cursor Right".
  * ASCII vertical tab is mapped (somewhat arbitrarily) to "Cursor Down".
  * ASCII form feed is mapped to "Clear Screen".
  * ASCII carriage return is mapped (somewhat arbitrarily) to "Cursor Left".
  * ASCII alert is mapped (arbitrarily) to $01 (unused by PETSCII).
  * An alternative mapping is provided for the internal ROM character mapping.
* TODO: Define the extension mechanism for custom character mappings and
  non-null-terminated string literals.

3.1.2 [Identifiers](https://port70.net/~nsz/c/c89/c89-draft.html#3.1.2)

* Number of significant characters in an internal identifier: limited only by
  available memory.
* Number of significant characters in an external identifier: limited only by
  available memory.
* External identifiers are case-sensitive.

3.1.2.5 [Types](https://port70.net/~nsz/c/c89/c89-draft.html#3.1.2.5)

* Chars are defined to be unsigned, since target platform has useful
  characters with the high bit set, and all values of characters must be
  positive.

4.10.4.5 [The system
function](http://port70.net/~nsz/c/c89/c89-draft.html#4.10.4.5)

* The system function must always return zero, since no command processor is
  available.

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