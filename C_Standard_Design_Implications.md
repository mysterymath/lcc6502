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

* Neither the Atari 800 (ATASCII) nor Commodore 64 (PETSCII) character sets
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
  * A function should be markable as an interrupt handler.
  * It must be possible to enable and disable interrupts.
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
  * If the value of such an object is used, it was set in some currently-active
    procedure.
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
* This means that the mechanism for controlling execution character sets needs
  to be visible to the preprocessor.
* LCC's preprocessor just uses the source character set, but it's easy to change in
  `cpp/eval.c` (line 502).
* A warning about long character constants in `cpp/eval.c` should be removed.
* The LCC compiler should be set so that wide characters are the same size as
  regular characters.
* String literals need not be strings (they can contain `'\0'` anywhere within),
  but the standard requires their value ends in a null character.
* The implementation should provide C-style null-terminated string literals,
  since there's no other way to achieve C89 compatibility.
* No mechanism is provided to change the default interpretation of character
  literals, since such literals would no longer work with routines designed
  for C strings.

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

3.5.2.1 [Struct and union specifiers](https://port70.net/~nsz/c/c89/c89-draft.html#3.5.2.1)

* From the LCC Manual:
  * Plain int bitfields are signed.
* See the [LCC bitfield experiments](lcc/experiments/bitfield/README.md) for
  LCC's behavior regarding bitfields.
  * In particular, LCC generates bit operations necessary to implement bitfields
    over arbitrary bytes. The compiler either needs to be altered or these need
    to be parsed to produce clear and set flag instructions whenever a bitfield
    associated with the processor flags register is accessed or mutated.
  * The compiler allocates bits little-endian (LSB first).
  * The compiler promotes bit-containing structs to ints when made an automatic
    variable (and possibly other cases), even though their sizeof is 1. This
    behavior should be altered, since 2 byte arithmetic is far more expensive.

3.4 [CONSTANT EXPRESSIONS](https://port70.net/~nsz/c/c89/c89-draft.html#3.4)

* Address constant expressions may be used in static initializers, and they
  refer to part or all of other static objects or functions.
* Constant expression evaluation is free to use the host arithmetic, so long as
  it is more precise than the target (not hard.)

3.5.3 [Type qualifiers](https://port70.net/~nsz/c/c89/c89-draft.html#3.5.3)

* Non-`volatile` `const` objects with statically-known values may be placed in
  ROM, and if their address is never used, they need not be allocated at all.
  This is actually true of any objects that has a statically-known value that
  can be proven never to be modified (const just ensures this).
* `volatile const` objects should not be placed in ROM and must be allocated,
  since the intent is that ASM code or hardware unknown to the C compiler should
  be able to modify the value.

3.5.7 [Initialization](https://port70.net/~nsz/c/c89/c89-draft.html#3.5.7)

* Aggregate types (arrays, structs, and unions) may only be initialized with
  constant expressions. This means that the byte sequence they are initialized
  to can always be determined at compile time.
* Unnamed struct or union fields need not be initialized.
* Static storage duration objects are intialized to zero if no other initializer
  is given.
* TODO: Determine how LCC performs initialization of structs.

3.6.6.4 [The return statement](https://port70.net/~nsz/c/c89/c89-draft.html#3.6.6.4)

* Return statements with no value are legal in functions with return values, so long
  as the return value is never used by the caller.

4.6 [NON-LOCAL JUMPS](https://port70.net/~nsz/c/c89/c89-draft.html#4.6)

* This implementation needs to define <setjmp.h>, since it may need significant
  compiler support to implement.

* Unlike other library functions, setjmp can be a only a macro. Trying to access
  it as a function (taking its address, etc.) is undefined behavior.

* The following forms are the only defined uses of setjmp:

  ```if/while/do-while (setjmp(<...>)) ```

  ```if/while/do-while (!setjmp(<...>)) ```

  ```if/while/do-while (setjmp(<...>) ==/!= <int const>) ```

  ```setjmp(<...>);```

* Life goes on after setjmp is called; various changes can be made to automatic
  variables in the setjmp-containing function. It's desirable that each variable
  has the exact value it had when longjmp was called, but this is difficult to
  achieve. If any of those automatic variables is in a register, then that
  register may have been saved and reused by some intervening function. But
  longjmp can't easily restore the saved value for that register, since it may
  be in an even deeper function. Most setjmp/longjmp implementations just save
  the values when *setjmp* was called, and restore those. This restores the
  value to that at the time *longjmp* was called, so long as they haven't
  changed since setjmp was called. The standard specifically allows this, so
  long as the automatic variables are not marked `volatile`. Volatile and static
  objects must have their values at the time of the longjmp, even if they have
  changed since the setjmp; with this approach, it usually means they cannot be
  stored in a register.

* Setjmp and longjmp can be slow, but they can't be so slow that they save and
  restore every single usable zero page address each time they are called.

* Longjmp needs to all return addresses (and anything else) off of the stack until
  the stack is restored to its state at the time of setjmp. Nothing need actually
  be changed, but the stack register must change. This is true for any soft stacks
  used as well; these soft stack pointers need to be reset.

* Longjmp provides an alternative way that an invocation of a function can be
  terminated. All invocations on the logical stack between the caller of setjmp
  and the call of longjmp are terminated. If an interrupt handler is terminated
  in this way, the computation that was occurring no longer matters; it can be
  considered abandoned. Thus, the flags that were pushed onto the stack by the
  interrupt handler no longer matter.

* Setjmp can only occur "up" the stack, never "down". Thus, the only way to
  longjmp into an interrupt handler is from inside a handler. This does not
  create any additional troubles.

4.8 [VARIABLE ARGUMENTS <stdarg.h>](https://port70.net/~nsz/c/c89/c89-draft.html#4.8)

* `va_start` and `va_arg` are macros, not functions.
* Variable argument functions can only be called in the presence of a prototype, so the compiler
  is always aware that such calls involve variable arguments. Thus, a totally different calling
  convention can be used.
* `va_start` includes the first non-variable argument as a parameter, but its use is totally optional.
* For efficiency, like with regular functions, the arguments should probably be passed in registers.
  * `va_start` can copy any registers used by the function to a register save area in the `va_list`.
  * The number of registers used can be passed as well, to allow only saving passed values.
  * Values that are not used need not be saved.
* The argument list can be scanned more than once, so the arguments need to be
  preserved, even after a traversal completes. The arguments need not be kept if
  the compiler can prove that no more than one traversal occurs.
* Each of these can be implemented in terms of magic compiler builtins.
  __builtin_va_arg returns a void* pointer that is cast to the corresponding
  type and indirected through in a macro. This pointer is not real; it will be
  completely removed by the code generator. The compiler will emit a warning if
  a void pointer is cast to a function type; this should be suppressed in this
  case, since the pointers don't actually "exist". This complexity saves
  creating a special compiler form, which is even more complex.

## TODO

* [ ] Resolve all outstanding TODO's.
* [ ] Ensure that all implementation-defined behaviors in the Appendix (A.6.3)
      are defined. Reorder them according to the Appendix.
* [ ] Group, reorder, and summarize the design implications by topic rather than
       by standard section.
* [ ] Scan through Embedded C Extensions
      [ISO/IEC TR 18037](http://www.open-std.org/JTC1/SC22/WG14/www/docs/n1169.pdf)