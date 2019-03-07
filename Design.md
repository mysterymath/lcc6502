# Design

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

* Return statements with no value are legal in functions with non-void return
    types, so long as the return value is never used by the caller.

* It must be possible to scan over the argument list of a variable argument
    function more than once.

* During a `longjmp`, it is legal to restore registers to their values at the
    time `setjmp` called so long as no register at that time contained the
    value of a volatile variable or a static object that could have changed
    since `setjmp` was called.

* Prototypes in library headers may only use identifiers in the reserved
    namespace: `__x` or `_X`.

* The number of registers saved by `setjmp` and restored by `longjmp` must be
    tightly bounded.

* `longjmp` must restore the interrupt disable flag to its value at the time of
    `setjmp`, since it may be used to escape from an interrupt.