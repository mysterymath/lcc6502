# Requirements

The C standard, the nature of the 6502, and the nature of each target
platform each impose a number of requirements for the design of a suitable
compiler. These requirements are gathered here, organized by topic.

## REQUIREMENTS

* In concert with an assembler, the compiler should be capable of producing a
  program that boots from the following kinds of Atari ROM cartridge:
  * 8KB
  * OSS one-chip 16 KB cartridge (Atari800 type 15)

* In concert with an assembler, the compiler should be capable of producing a
    program that boots from an Atari 800 cassette.

* In concert with an assembler, the compiler should be capable of producing a
    program that boots from an Atari 800 diskette.

* In concert with an assembler, the compiler should be capable of producing a
    program that minimally boots from an Atari 800 diskette, loads the rest of
    itself, then runs the code that it loaded.

* In concert with an assembler, the compiler should be capable of producing a
    program that `RUN`s when `LOAD`ed from a Commodore 64 disk.

* In concert with an assembler, the compiler should be capable of producing a
    program that boots from a Commodore 64 cartridge.

* The compiler must provide a means for the user to specify what address
    regions (including Zero Page) are available for use by the compiler. This
    must include which address regions are RAM or ROM and the number of banks
    available at various address regions. The compiler must produce code and
    data that resides in those address regions, such that the code produced
    can be included into an assembly program that describes the full program.

* The compiler should produce code that runs correctly on either a NMOS or CMOS
    6502.

* The system should be ANSI C compliant for a freestanding implementation.

## DESIGN

On the face of it, paging conflicts with the C89 requirement that any two
pointers that compare equal point to the same object. Accordingly:

* Paging functionality should be considered an extension of the standard and
    must be explicitly requested by the user.

* Comparing two pointers that refer to objects in regions with overlapping
    memory assignments is undefined behavior.

TODO: Add both of these to Implementation-Defined behavior, along with a
description of the resource specification mechanism.

* The compiler should emit a branch to an absolute JMP if a branch needs to
    travel more than 127 bytes forward or more than 128 bytes backward. This
    should be incorporated into the cost model.

* The compiler should consider branches taken one cycle more expensive than
    branches not taken in its cost model.

* A number of instructions are one cycle more expensive when they cross page
    boundaries; this should be incorporated into the cost model.

* The system should not emit any indirect JMPs through a vector ending with FF,
    since the NMOS versions of the 6502 have a bug. Avoiding the scenario
    entirely allows easy compatibility with both the NMOS and CMOS versions
    of the chip.

* Indexed zero page accesses are vulnerable to 8-bit wraparound. If this would
    produce incorrect behavior, the compiler should use the absolute address
    mode and update the cost model accordingly.

* The compiler should avoid placing any addresses that will be indirected
    through on the 0xFF-0x100 boundary.

* Any tables using the `(,X)` addressing mode must be ensured to fit entirely
    on the zero page.

* Indexed addressing modes that cross page boundaries (start address + index is
    not at the same 256-byte page as the start address) issue an erroneous
    read from the old page, exactly 256 bytes prior to the correct address.
    The compiler must ensure that only addresses controlled by the compiler
    are accessed in such a way.

* The compiler should not use read-modify-write instructions like INC with
    volatile types.

* Mutable static objects need to be copied from ROM to RAM locations. These RAM
    locations would be the canonical locations for the objects.

* Objects with statically-known constant values whose addresses are never used
    need not be allocated.

* Static-lifetime objects that can be proven to neither be accessed using
    `volatile` nor mutated can be allocated in ROM.

* Address constant expressions may be used in static initializers, and they
    refer to part or all of other static objects or functions. These may even
    be self-referential; for instance, a static struct with a recursive
    pointer can refer to its own address.

* Automatic objects that can be proven never to be present in two
    simultaneously active invocations can be treated like static objects, with
    one exception. If the objects were initialized, the initialization still
    needs to happen each time, unlike other statics, which are initialized before
    program startup.

* Values of pointers to auto objects in terminated blocks are indeterminate.
    This means that objects in blocks that cannot be simultaneously active
    can safely share the same pointer value. This includes if they are
    treated like statics via the above.

* When a stack is used, it's simplest (and fastest) to only bump the stack
    pointer once at the beginning of a function. Otherwise, any goto
    statements that enter a block need to allocate all the space required for
    that block.

* The preprocessor needs to be modified to understand the target character set,
    since character literals can be used in constant expressions for conditional
    compilation.

  * LCC's preprocessor currently just uses the source character set, but it's
    easy to change in `cpp/eval.c` (line 502).

* An LCC warning about long character constants in `cpp/eval.c` should be
    removed.

* The implementation should probably use Berkely SoftFloat v2, since:

    * It's very easy to port to new platforms, even those with odd int sizes.

    * It's IEEE 754 compliant, and supports binary32 and binary64.

    * It has a sufficiently permissive license.

    * TODO: A notice must be included somewhere in the standard library source
        that the standard library is a deriviative work of the Berkeley SoftFloat
        library.

    * The later versions (v3) require the target to support 64-bit integers.

* Automatic structure variable initializers are static objects emitted by LCC.
    Identical versions of these objects should be coalesced into one to save
    space.

* Zero initializers for automatic structure variables should be replaced with a
    memset or equivalent.

* Bit-field operations that involve 8 or fewer bits should be strenth-reduced
    to one byte from LCC's full integer operations.

## END DESIGN

## OLD REQUIREMENTS

## Data

### Structs and Unions

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

The BRK instruction can be swallowed in NMOS chips if a hardware interrupt
occurs while one is being fetched. This was corrected in the CMOS
implementation. To avoid this complexity, and due to insufficient utility, the
BRK instruction should not be used by the compiler.

IRQ handlers already have the A register saved, but not the X or Y registers.
To allow C functions to be called by the OS, customizable callee-save
register sets are required.

Given the above, an interrupt handler also needs to restore registers it did
not save (A) before executing a RTI.

The system timers are called in the context of an interrupt via a JSR. These
must end in an RTS, but all registers are already saved. Note that these do
not need to restore the other registers before RTS, unlike the above. They
still must not clobber anything in use by an interrupted function. Thus
customizable calling conventions are needed for "regular" functions too.

TODO: Redefine the __interrupt() mechanism to accomodate this.

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

Return statements with no value are legal in functions with non-void return
types, so long as the return value is never used by the caller.

#### System Calls

The Atari 800 provides a number of OS routines with their own calling
conventions. The compiler should allow C code to call these somehow.

TODO: Determine the mechanism once all examples have been collected.

Calling CIO routines involves first setting up a set of IOCB memory locations
to the proper value, then setting the X register IOCB number times 16 in the
X register, and then possibly setting the A register a data byte. A JSR to
the CIO entry point is then issued. Afterward, the X register is unchanged,
but the Y register is set to an error status. The condition flags Zero and
Negative of the processor reflect the value in the Y register. The IOCB
memory locations are also updated to reflect the number of bytes written,
status, etc.

Calling resident I/O handlers without going through CIO requires jumping to
an address given by an entry in a table of addresses provided by the OS.
However, each address is one less than it should be. This is to facilitate
pushing the address on the stack, then using RTS to jump to the address.
(This is smaller but slower than loading the address into the zero page and
using an indirect JMP.) RTS adds one to the address it takes off the stack to
move the PC to the instruction after the corresponding JSR. The compiler
needs to support using RTS to execute this kind of indirect jump.

Implementing a CIO handler requires taking arguments from a number of places:
the A, X, and Y registers, as well as an IOCB in page 0 named ZIOCB.

When calling KERNAL routines, the Commodore 64 uses the CARRY bit to indicate
whether a error occurred. The A register contains the error number if set.

The A, X, and Y registers are variously used for input and output of KERNAL
routines.

As far as can be determined, neither the OS of the Commodore 64 nor the Atari
800 require passing zero page locations to routines. Thus, no special C
support need be provided for zero-page-only variables. If necessary, these
can be done in assembly language. (Save the contents of a zero page location,
use it, and restore. C is none the wiser.)

#### Variable-Sized Argument Lists

`va_start` and `va_arg` are macros, not functions.

Variable argument functions can only be called in the presence of a prototype,
so the compiler is always aware that such calls involve variable arguments.
Thus, a totally different calling convention can be used.

`va_start` includes the first non-variable argument as a parameter, but its use
is totally optional.

For efficiency, like with regular functions, the arguments should probably be passed in registers.

va_start can copy any registers used by the function to a register save area
in the `va_list`. The number of registers used can be passed as well, to allow
only saving passed values. Values that are not used need not be saved.

The argument list can be scanned more than once, so the arguments need to be
preserved, even after a traversal completes.

Each of these can be implemented in terms of magic compiler builtins.
__builtin_va_arg returns a void* pointer that is cast to the corresponding type
and indirected through in a macro. This pointer is not real; it will be
completely removed by the code generator. The compiler will emit a warning if a
void pointer is cast to a function type; this must be suppressed in this
case, since the pointers don't actually "exist". This complexity saves creating
a special compiler form, which is even more complex.

#### switch Statements

At least 257 case labels need to be supported (C89 2.2.4.1). This precludes
creating a sort of byte-indexed perfect-hashed jump table, since there would be
too many entries in the worst case. This is to allow branching on any character
as well as EOF.

#### setjmp/longjmp

This implementation needs to define <setjmp.h>, since it may need significant
compiler support to implement.

Unlike other library functions, setjmp can be a macro without a corresponding
external identifier. Trying to access it as a function (taking its address,
etc.) is undefined behavior. Additionally, the following forms are the only
defined uses of setjmp:
* ```if/while/do-while (setjmp(<...>))```
* ```if/while/do-while (!setjmp(<...>))```
* ```if/while/do-while (setjmp(<...>) ==/!= <int const>)```
* ```setjmp(<...>);```

Life goes on after setjmp is called; various changes can be made to automatic
variables in the setjmp-containing function. It's desirable that each variable
has the exact value it had when longjmp was called, but this is difficult to
achieve. If any of those automatic variables is in a register, then that
register may have been saved and reused by some intervening function. But
longjmp can't easily restore the saved value for that register, since it may be
in an even deeper function.

To solve the this dilemma, most setjmp/longjmp implementations just save the
values when *setjmp* was called, and restore those. This is correct if and only
if the values have not changed since setjmp was called. The standard
specifically allows this, so long as the automatic variables are not marked
`volatile`. Volatile automatic objects and static objects must have their
values at the time of the longjmp, even if they have changed since the setjmp;
accordingly, they cannot easily be stored in a register in any function that
can call setjmp.

It's OK for setjmp and longjmp to be fairly slow, but they can't be so slow
that they save and restore every single usable zero page address each time they
are called. This complicates naively using zero page addresses as registers.

Longjmp needs to pop all return addresses (and anything else) off of the stack
until the stack is restored to its state at the time of setjmp. Nothing need
actually be changed, but the stack register must change. This is true for any
soft stacks used as well; these soft stack pointers need to be reset.

Longjmp provides an alternative way that an invocation of a function can be
terminated. All invocations on the logical stack between the caller of setjmp
and the call of longjmp are terminated. If an interrupt handler is terminated
in this way, the computation that was occurring no longer matters; it can be
considered abandoned. Thus, the flags that were pushed onto the stack by the
interrupt handler no longer matter. The processor should remain in the state it was in when the longjmp was issued; including the interrupt enable flag.

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

