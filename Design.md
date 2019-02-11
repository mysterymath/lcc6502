# Design

* The compiler must emit a branch to an absolute JMP if a branch needs to
    travel more than 127 bytes forward or more than 128 bytes backward. This
    must be incorporated into the cost model.

* The compiler should consider branches taken one cycle more expensive than
    branches not taken in its cost model.

* A number of instructions are one cycle more expensive when they cross page
    boundaries; this should be incorporated into the cost model.

* The system must not emit any indirect JMPs through a vector ending with FF,
    since the NMOS versions of the 6502 have a bug. Avoiding the scenario
    entirely allows easy compatibility with both the NMOS and CMOS versions
    of the chip.

* Indexed zero page accesses are vulnerable to 8-bit wraparound. If this would
    produce incorrect behavior, the compiler must use the absolute address
    mode and should update the cost model accordingly.

* The compiler must avoid placing any addresses that will be indirected
    through on the 0xFF-0x100 boundary.

* Any tables using the `(,X)` addressing mode must be ensured to fit entirely
    on the zero page.

* Indexed addressing modes that cross page boundaries (start address + index is
    not at the same 256-byte page as the start address) issue an erroneous
    read from the old page, exactly 256 bytes prior to the correct address.
    The compiler must ensure that only addresses controlled by the compiler
    are accessed in such a way.

* The compiler must not use read-modify-write instructions like INC with
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

* The implementation should probably use Berkeley SoftFloat v2, since:

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

* Bit-field operations that involve 8 or fewer bits must be strength-reduced
    to one byte from LCC's full integer operations.

* Automatic variables must retain their values across signals and or interrupts.

* The BRK instruction should not be used by the compiler.

* Return statements with no value are legal in functions with non-void return
    types, so long as the return value is never used by the caller.

* Prototyped functions with no "narrow" types (smaller than int) and no variable
    argument list must be callable in translation units without the
    prototype.

* It must be possible to scan over the argument list of a variable argument         function more than once.

* During a `longjmp`, it is legal to restore registers to their values at the
    time `setjmp` called so long as no register at that time contained the value
    of a volatile variable or a static object that could have changed since `setjmp` was called.

* Prototypes in library headers may only use identifiers in the reserved
    namespace: `__x` or `_X`.

* The compiler must provide a means for the user to specify what address
    regions (including Zero Page) are available for use by the compiler. This
    must include which address regions are RAM or ROM and the number of banks
    available at various address regions. The compiler must produce code and
    data that resides in those address regions, such that the code produced
    can be included into an assembly program that describes the full program.

* The register save and restore overhead for every call, even those crossing a
  C/assembly boundary, must be small and finite. This is particularly true when calling a C function from an interrupt handler.

* The implementation must define <setjmp.h> suitable for a hosted
    implementation of ANSI C, though only a freestanding implementation is
    provided.

* The number of registers saved by `setjmp` and restored by `longjmp` must be
    tightly bounded.

* `longjmp` must restore the interrupt disable flag to its value at the time of
    `setjmp`, since it may be used to escape from an interrupt.