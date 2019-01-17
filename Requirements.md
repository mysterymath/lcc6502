# Requirements

The C standard, the nature of the 6502, and the nature of each target platform
will impose a number of requirements for the design of a compiler. These requirements are gathered here, organized by topic.

## Data

### ROM

Objects in static storage need to be initialized *before* program startup
(C89 2.1.2). For ROM output, this means that mutable static objects need to be
copied to RAM locations. These would become the canonical locations for the
objects.

Non-`volatile` `const` objects with statically-known values may be placed in
ROM, and if their address is never used, they need not be allocated at all.
This is actually true of any objects that has a statically-known value that can
be proven never to be modified (`const` just ensures this).

`volatile const` objects should not be placed in ROM and must be allocated,
since the intent is that ASM code or hardware unknown to the C compiler should
be able to modify the value.

### Constant Expressions

Address constant expressions may be used in static initializers, and they refer
to part or all of other static objects or functions. These may even be
self-referential; for instance, a static struct with a recursive pointer can
refer to its own address.

Constant expression evaluation is free to use the host arithmetic, so long as
it is more precise than the target (not hard.)

### Automatic Storage

Automatic objects that can be proven never to be present in two simultaneously
active invocations can be treated much like static objects.  If the objects
were initialized, the initialization still needs to happen each time, unlike
other statics, which are initialized before program startup.  If the value of
such an object is used, it was set in some currently-active procedure; such
values cannot by their nature persist between calls.

Values of pointers to auto objects in terminated blocks are indeterminate.
This means that objects in blocks that cannot be simultaneously active can
safely share the same pointer value.

It's simplest to only bump the stack pointer once at the beginning of a
function. Otherwise, any goto statements that enter a block need to allocate
all the space required for that block.

## Volatile

Reads from volatile objects need to be treated differently than regular reads,
so that information needs to be extacted from LCC (C89 2.1.2.3).

### Characters

Escape characters should not output a printable character.

Alert must not change the cursor position.

Carriage return should move the cursor to the initial position of the current
line.

Sign extending chars is expensive on the 6502, and at least one major POSIX
platform (ARM) does not sign extend chars. Thus, the implementation, like ARM,
defines `CHAR_MIN` to be `0` and `CHAR_MAX` to be the same as `UCHAR_MAX`.

The preprocessor needs to be modified to understand the target character set,
since character literals can be used in constant expressions for conditional
compilation. This means that the mechanism for controlling execution character
sets needs to be visible to the preprocessor.

LCC's preprocessor currently just uses the source character set, but it's easy
to change in `cpp/eval.c` (line 502).  A warning about long character constants
in `cpp/eval.c` should also be removed.

The LCC compiler should be set so that wide characters are the same size as
regular characters, since nobody is going to care about wide characters on this
platform.

## Floating Point

The impelementation should probably use Berkely SoftFloat v2, since:
* It's very easy to port to new platforms, even those with odd int sizes.
* It's IEEE 754 compliant, and supports binary32 and binary64.
* It has a sufficiently permissive license.
  * TODO: A notice must be included somewhere in the standard library source
    that the standard library is a deriviative work of the Berkeley SoftFloat
    library.
* The later versions (v3) require the target to support 64-bit integers.

### Structs and Unions

LCC performs struct initialization much like character array initialization.
Space for the initializer is statically allocated, and an assignment is issued
at the beginning of the block from the static location to the variable. This
works because aggregate types can only be initialized with compile-time
constants. LCC does not combine identical initializers; instead, it creates one
initializer per struct literal instance in the source text.

Identical initializers can be easily detected in the backend. This should be
done, since it will save precious space.

#### Bit-Fields

See the [LCC bit-field experiments](lcc/experiments/bitfield/README.md) for
LCC's behavior regarding bit-field.

In particular, LCC generates bit operations necessary to implement bit-field
over arbitrary bytes. The compiler always accesses bit-fields as
2-byte ints, even if the entire struct is only one byte long. When a
bit-field is modified, all data outside the bit-field is read and written back
unmodified. This means that writing to a bit-field can modify data outside of
the struct, even if that data is marked volatile.

Volatile just means that the compiler must access the value whenever the
program says to, not that the compiler must ensure that it never touches such
an object except when the program says so. This has been a point of contention
in the C community. The backend should always be able to lower such accesses to
1 byte. This is both faster and less surprising. The confusing behavior can
still occur if a volatile bit-field is next to a non-volatile one in the same
struct.

## Code

### Signals/Interrupts

Automatic variables need to retain their values across signal handling
suspensions (C89 2.1.2.3). This implies either keeping them in no-clobber registers
or saving them on a stack.

No signals need be provided, but to allow implementing signals, intterupt
handlers must be writable in pure C. Any function can be interrupted at any
time by an interrupt, which can call any C function.

Interrupt handlers must not overrite any locations (memory or register) used by
previous invocations or by any active functions.

Interrupt handlers often need to be extremely timely, so the number of
locations saved and restored by the handler must be tightly bounded.

### Code Size

For many practical programs, it may be difficult to fit the program and its
data into available RAM. A program may reserve space for data using static
variables.

Since the target machines do not have Memory Management Units, much of the
address space is unavailable for use by the program. The compiler should pack
the program and its data into the available RAM as tightly as possible. Some
programs may still be too big to fit; these may be rejected.

No optimizations (inlining, etc) may be performed unless it can be guaranteed
that it will not cause a program to no longer fit into RAM. Note that many
optimizations tend to reduce both code size and execution time. When
optimization is enabled, the compiler should always aim for the most efficient
program that can be made to fit.

### Functions

Each function needs to support at least 31 arguments (C89 2.2.4.1). That's at least
31 bytes of storage.

Prototyped functions with no "narrow" types (smaller than int) and no variable
argument list must be callable in translation units without the prototype.

Varargs functions may only be called through a prototype.

Return statements with no value are legal in functions with non-void return
types, so long as the return value is never used by the caller.

### Switch Statements

At least 257 case labels need to be supported (C89 2.2.4.1). This precludes
creating a sort of byte-indexed perfect-hashed jump table, since there would be
too many entries in the worst case. This is to allow branching on any character
as well as EOF.

## Libraries

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

## End new content

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
