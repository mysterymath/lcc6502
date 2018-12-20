# Design Implications from the C89 Standard

The standard will impose a number of constraints for the design of a compiler
for the 6502. When they can be directly derived from some requirement of the
standard, those constraints are listed here. This document is organized in
parallel to the standard, section for section.

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
  changing one `.c` file only requires recompiling that one file), much of the C
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

* At program startup, the routine with the name `_start` is called. This
  function must take no arguments and have a void return type.

2.1.2.3 [Program execution](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.2.3.)

* Reads from volatile objects need to be treated differently, so that information needs to
  be extacted from LCC.
* Automatic variables need to retain their values across signal handling
  suspensions. This implies either keeping them in no-clobber registers or
  saving them on a stack.

2.2.1 [Character sets](https://port70.net/~nsz/c/c89/c89-draft.html#2.2.1)

* Neither  their Atari 800 (ATASCII) or Commodore 64 (PETSCII) character sets
  contain `'{'` or `'}'`, which are both required by the standard for both source
  and execution environments.
* At least one target character set, ATASCII, does not contain a null character
  at zero. This means it cannot simply support null-terminated strings.
* Neither of the character ROM encodings for ATASCII and PETSCII have a null
  character at zero.

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
  defines `CHAR_MIN` to be `0` and `CHAR_MAX` to be the same as `UCHAR_MAX`.

3.1.2.1 [Scopes of identifiers](https://port70.net/~nsz/c/c89/c89-draft.html#3.1.2.1)

* The backend needs to obtain scoping information from LCC, so that otherwise
  identical identifiers with different scope in LCC's output do not conflict
  with one another.

* The following declaration has block scope, even though it refers to an external
  function:
  ```C
  {
    extern int f();
  }
  ```
  TODO: Determine LCC's behavior in this case.

* Prototypes in library headers may only use identifiers in the reserved
  namespace (`__x` or `_X`). Otherwise, the user could place a #define macro before
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

3.1.3.4 [Character constants](https://port70.net/~nsz/c/c89/c89-draft.html#3.1.3.4)

* The preprocessor needs to be modified to understand the target character set,
  since character literals can be used in constant expressions for conditional
  compilation.
* This means that the mechanism for controlling character set selection needs to
  be visible to the preprocessor. Probably some kind of #pragma.
* TODO: Go through the relevant LCC source, see if this is possible.
* TODO: Determine what LCC does with wide character literals.
* String literals need not be strings (they can contain `'\0'` anywhere within),
  but the standard requires their value ends in a null character.
* The implementation should provide C-style null-terminated string literals,
  since there's no other way to achieve C89 compatibility.
* The implementation should provide a way to define such macros and their
  corresponding mappings from ASCII to execution character sets.
* No mechanism is provided to change the default interpretation of character
  literals, since such literals would no longer work with routines designed
  for C strings. This behavior is sufficiently dangerous to require explicit
  denotation in the source text.

3.2.1.5 [Usual arithmetic conversions](https://port70.net/~nsz/c/c89/c89-draft.html#3.2.1.5)

|               | Int  | Unsigned Int | Long | Unsigned Long | Float | Double |
| ------------- | ---- | ------------ | ---- | ------------- | ----- | ------ |
| Int           | Int  | Unsigned Int | Long | Unsigned Long | Float | Double |
| Unsigned Int  | X    | Unsigned Int | Long | Unsigned Long | Float | Double |
| Long          | X    | X            | Long | Unsigned Long | Float | Double |
| Unsigned Long | X    | X            | X    | Unsigned Long | Float | Double |
| Float         | X    | X            | X    | X             | Float | Double |
| Double        | X    | X            | X    | X             | X     | Double |

3.3.2.2 [Function Calls](https://port70.net/~nsz/c/c89/c89-draft.html#3.3.2.2)

* If a function without a prototype is called, integral promotions occur on
  each argument and floats are converted to doubles. This also occurs on each
  argument in a `...` section of a prototype. For this platform, this means
  that the standard requires that printf() exclusively take 16-bit ints and
  64-bit doubles.
* At each call site, the number of arguments to a variable argument call is
  statically known.
* Prototyped functions with no "narrow" types and no variable argument list
  must be callable in translation units without the prototype.
* Varargs functions may only be called through a prototype.

## TODO

* [ ] Section 3.3.8+
* [ ] Determine precisely when volatiles are accessed. Use GCC as
      [reference](https://gcc.gnu.org/onlinedocs/gcc/Volatiles.html#Volatiles).
* [ ] Ensure that all implementation-defined behaviors in the Appendix (A.6.3)
      are defined.
* [ ] Scan through Embedded C Extensions
      [ISO/IEC TR 18037](http://www.open-std.org/JTC1/SC22/WG14/www/docs/n1169.pdf)