# Implementation-Defined Behavior Rationale

This document gives the rationale for the
[Implementation_Defined_Behavior.md](implementation-defined behavior). It is
organized in parallel with the IBD document, section for section.

## A.6.3.3 Characters

### The mapping of members of the source character set (in character constants and string literals) to members of the execution character set (3.1.3.4)

The character mappings were chosen to be the closest possible mapping that has as many of the following properties as possible:

* Escape characters do not output printable characters.

* Alert does not change the cursor position.

* Carriage return moves the cursor to the initial position of the current line.

These properties are not generally attainable on the target platform, but
they are not strictly required by the standard. The spirit of the properties
were retained as much as possible.

### Whether a 'plain' char has the same range of values as signed char or unsigned char (3.2.1.1)

Sign extending chars is expensive on the 6502, and at least one major POSIX
platform (ARM) does not sign extend chars. Thus, the implementation, like
ARM, makes 'plain' `char` unsigned.

## A.6.3.12 Preprocessing directives

### Whether the value of a single-character character constant in a constant expression that controls conditional inclusion matches the value of the same character constant in the execution character set. Whether such a character constant may have a negative value (3.8.1)

Though the standard allows the preprocessor to use either the source or
target character set, consistency with GCC requires the target character set
be used.

## Extensions

### Assembly Language Interop

Without making severe assumptions about what external routines can do, a
great many optimizations that humans expect the compiler should be able to do
become impossible. For example, say the `main` function is called by an
external `start` routine, and `main`, through some chain of descendants,
calls an external `IO` routine. Since the compiler cannot prove that `IO`
does not call `start` or `main`, it cannot prove that the whole program is
not recursive, which forces the use of a stack. A human programmer could
easily verify that the function is not recursive, but a compiler cannot
reliably verify the control flow of arbitrary assembly. Accordingly, the
programmer needs to provide the compiler with all necessary side effect and
control flow information.