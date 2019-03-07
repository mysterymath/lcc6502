# Design

* When a stack is used, it's simplest (and fastest) to only bump the stack
    pointer once at the beginning of a function.

* The preprocessor should use the target character set for consistency w/ GNU.

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

* Identical versions of automatic structure variable initializers emitted by
    LCC should be coalesced into one to save space.

* Zero initializers for automatic structure variables should be replaced with a
    memset or equivalent.

* Bit-field operations that involve 8 or fewer bits must be strength-reduced
    to one byte from LCC's full integer operations.

* The number of registers saved by `setjmp` and restored by `longjmp` must be
    tightly bounded.

* `longjmp` must restore the interrupt disable flag to its value at the time of
    `setjmp`, since it may be used to escape from an interrupt.