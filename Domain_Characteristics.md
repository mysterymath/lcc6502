# Domain Characteristics

This document contains characteristics of the 6502 (NMOS and CMOS), the Atari
800, the Commodore 64, and the C programming language that are non-obvious
and constrain the space of possible solutions.

## C Language

Address constant expressions may be used in static initializers, and they
refer to part or all of other static objects or functions. These may even be
self-referential; for instance, a static struct with a recursive pointer can
refer to its own address.

Values of pointers to auto objects in terminated blocks are indeterminate.

If the stack pointer(s) are increased inside a block that is not the entry
block of the function, then any goto's that jump inside that block must also
ensure that space is allocated. Alternatively, the standard allows all space
to be reserved at the beginning of a function.

The C preprocessor can evaluate the numeric value of character constants, so
it needs to be character set aware. GNU-like compilers use the execution
character set in the preprocessor, but the standard allows either the source
or execution character sets to be used.

Return statements with no value are legal in functions with non-void return
types, so long as the return value is never used by the caller.

It must be possible to scan over the argument list of a variable argument
function more than once.

During a `longjmp`, it is legal to restore registers to their values at the
time `setjmp` called so long as no register at that time contained the value
of a volatile variable or a static object that could have changed since
`setjmp` was called.

Prototypes in library headers may only use identifiers in the reserved
namespace (`__x` or `_X`). Otherwise, the user could place a #define macro
before the header as follows:

```C
#define status []
void exit(int status);
```

This becomes:

```C
void exit(int []);
```

## LCC Compiler

LCC's preprocessor currently uses the source character set, but it's
easy to change in `cpp/eval.c` (line 502).

Automatic structure variable initializers are static objects emitted by LCC.
One is emitted per source location; duplicates are not coalesced. This is also
true if the initializer is all zeroes; LCC does not special case this.

LCC performs bit-field operations using type "int"; even if the bitfield
granularity is 8 bits.