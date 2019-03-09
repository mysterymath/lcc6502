# Implementation-Defined Behavior

The C89 standard requires a conforming implementation to document a number of
"implementation-defined" behaviors and characteristics. All such behaviors and
characteristics are defined here. This document is organized according to
Appendix A.6.3 of the standard. All extensions to the C language provided by the
compiler are also described here.

## Definitions

### Limited only by memory

The compiler will attempt to allocate sufficient RAM on the compiling machine to
support any construct given by the user; compilation will only fail if
insufficient RAM is available.

### Round to nearest; even

The value is rounded to the nearest representable value, and if the value to be
rounded equidistant between two representable values, it is rounded to the one
that is even (i.e., the lowest order bit is zero).

## A.6.3.1 Environment

* The name and type of the function called at program startup (2.1.2.1).

  * Upon program startup, an external function `main` is called. This function
    must have no arguments and return void.

* What library facilities are available to a freestanding program (2.1.2.1).

  * No additional library facitilies are provided beyond those required by the standard.

## A.6.3.2 Identifiers

* The number of significant initial characters (beyond 31) in an identifier without external linkage (3.1.2).

  * [Limited only by memory](#Limited-only-by-memory).

* The number of significant initial characters (beyond 6) in an identifier with external linkage (3.1.2).

  * [Limited only by memory](#Limited-only-by-memory).

* Whether case distinctions are significant in an identifier with external linkage (3.1.2).

  * Case distinctions are significant.

## A.6.3.3 Characters

* The members of the source and execution character sets, except as explicitly specified in the Standard (2.2.1).

  * The source character set is ASCII for all targets.

  * For the Atari 800 the execution character set is ATASCII, minus the heart
    character present at zero.

  * For the Commodore 64 the execution character set is shifted PETSCII.

* The shift states used for the encoding of multibyte characters (2.2.1.2).

  * No shift states are used.

* The number of bits in a character in the execution character set (2.2.4.2).

  * There are 8 bits per character.

* The mapping of members of the source character set (in character constants and string literals) to members of the execution character set (3.1.3.4).

  * The preprocessor and compiler both map character literals to the values that
    they have on the target machine.
  
  * For the Atari 800 characters are mapped to ATASCII naturally, except the following:
    * ASCII '{' is mapped to inverse '['.
    * ASCII '}' is mapped to inverse ']'.
    * ASCII '~' is mapped to inverse '-'.
    * ASCII vertical tab is mapped (somewhat arbitrarily) to "Cursor Down".
    * ASCII form feed is mapped to "Clear Screen".
    * ASCII alert is mapped to "Buzzer".
    * ASCII carriage return is mapped (somewhat arbitrarily) to "Cursor Left".

  * For the Commodore 64 characters are mapped to shifted PESTCII naturally, except the following:
    * ASCII '^' is mapped to '↑'.
    * ASCII '\' is mapped to '£'.
    * ASCII '|' is mapped to 0x7D.
    * ASCII '~' is mapped to 0xAE.
    * ASCII '{' is mapped to 0xAB.
    * ASCII '}' is mapped to 0xB3.
    * ASCII tab is mapped (somewhat arbitrarily) to "Cursor Right".
    * ASCII vertical tab is mapped (somewhat arbitrarily) to "Cursor Down".
    * ASCII form feed is mapped to "Clear Screen".
    * ASCII carriage return is mapped (somewhat arbitrarily) to "Cursor Left".
    * ASCII alert is mapped (arbitrarily) to $01 (unused by PETSCII).

* The value of an integer character constant that contains a character or escape sequence not represented in the basic execution character set or the extended character set for a wide character constant (3.1.3.4).

  * ASCII characters without naturally corresponding characters in the execution
    character set are mapped via their numeric value in ASCII. This is true even
    if this results in multiple ASCII characters mapping to the same execution
    character.

* The value of an integer character constant that contains more than one character or a wide character constant that contains more than one multibyte character (3.1.3.4).

  * Additional characters beyond the first are ignored and a diagnostic is issued.

* The current locale used to convert multibyte characters into corresponding wide characters (codes) for a wide character constant (3.1.3.4).

  * The current locale is always the "C" locale.

* Whether a 'plain' char has the same range of values as signed char or unsigned char (3.2.1.1).

  * `char`s are defined to be unsigned, since target platform has useful
    characters with the high bit set, and all characters' values must be
    positive.

## A.6.3.4 Integers

* The representations and sets of values of the various types of integers (3.1.2.5).

  * An short consists of 2 little-endian bytes.
  * An int consists of 2 little-endian bytes.
  * A long consists of 4 little-endian bytes.
  * For the value ranges of each type, see [limits.h](include/limits.h)

* The result of converting an integer to a shorter signed integer, or the result of converting an unsigned integer to a signed integer of equal length, if the value cannot be represented (3.2.1.2).

  * When an integer is converted to a signed integral type that cannot represent
    its value, the bytes of the source integer are reinterpreted as those of the
    target type. If the target type is smaller, only the lower-order byte(s) are
    considered.

* The results of bitwise operations on signed integers (3.3).

  * Bitwise operators on signed types produce the result of first converting to
    the corresponding unsigned type, then applying the operator, then converting
    back to the corresponding signed type.

* The sign of the remainder on integer division (3.3.5).

  * When exactly one of the operators to the `/` operator is negative, the
    result is the smallest integer greater than the algebraic quotient. This
    "round towards zero" behavior mimics FORTRAN and the later C99 standard.

* The result of a right shift of a negative-valued signed integral type (3.3.7).

  * Right shifts of signed values are arithmetic, not logical. That is, the sign
    bit is copied to fill in the empty space left by shifting the other bits
    right. Though this is not required by the C89 standard, and though it is
    slower on the 6502 than logical shifts, breaking convention with nearly
    every other C implementation would burden portability of existing C code.

## A.6.3.5 Floating point

* The representations and sets of values of the various types of floating-point numbers (3.1.2.5).

  * A float consists of 4 bytes encoded using the IEEE 754 binary32 format.
  * A double consists of 8 bytes encoded using the IEEE 754 binary64 format.
  * For the value ranges of each type, see [limits.h](include/limits.h)

* The direction of truncation when an integral number is converted to a floating-point number that cannot exactly represent the original value (3.2.1.3).

  * [Round to nearest; even](#Round-to-nearest;-even).

* The direction of truncation or rounding when a floating-point number is converted to a narrower floating-point number (3.2.1.4).

  * [Round to nearest; even](#Round-to-nearest;-even).

## A.6.3.6 Arrays and pointers

* The type of integer required to hold the maximum size of an array --- that is, the type of the sizeof operator, size_t (3.3.3.4, 4.1.1).

  * `unsigned int`

* The result of casting a pointer to an integer or vice versa (3.3.4).

  * Pointers may be converted to int, unsigned int, long, and unsigned long. The
    value is the address of the referenced object, expressed as an unsigned int,
    then converted to the target type. Null pointers produce zero values.
  * Any integral value may be converted to a pointer. The value is first
    converted to an unsigned int. Then, the pointer refers to a virtual object
    at the memory location with corresponding address. This is true even for 0.
  * Virtual objects behave like objects with static storage duration, except:
    * Virtual objects have undefined value at program startup.
    * If any non-virtual object's storage overlaps with a virtual object,
      accessing the virtual object is undefined behavior.
  * The compiler will never place an object at location zero, so it is still true
    that a null pointer will never compare equal to any object. However, it may
    equal a virtual object.
  * The above implies that dereferencing a null pointer is *not* undefined
    behavior on this platform.
  * If an integral value is converted to a function pointer, the pointer type
    must have void return type and void arguments. The integral value is
    converted to an unsigned int to determine an address. Calling the pointed-to
    function is equivalent to issuing a JSR instruction to that address.

* The type of integer required to hold the difference between two pointers to members of the same array, ptrdiff_t (3.3.6, 4.1.1).

  * `int`

## A.6.3.7 Registers

* The extent to which objects can actually be placed in registers by use of the register storage-class specifier (3.5.1).

  * The `register` storage class has no effect on the output of the compiler
    beyond that mandated by the standard.

## A.6.3.8 Structures, unions, enumerations, and bit-fields

* A member of a union object is accessed using a member of a different type (3.3.2.3).

  * The relevant bytes of the union are reinterpreted as the type used for the access.

* The padding and alignment of members of structures (3.5.2.1). This should present no problem unless binary data written by one implementation are read by another.

  * No alignment or padding is used, since the 6502 has no alignment requirements.

* Whether a 'plain' `int` bit-field is treated as a `signed int` bit-field or as
  an `unsigned int` bit-field (3.5.2.1).

  * `signed int`.

* The order of allocation of bit-fields within an `int` (3.5.2.1).

  * From low-order bits to high-order bits within a byte (little-endian bit
    order).

* Whether a bit-field can straddle a storage-unit boundary (3.5.2.1).

  * They cannot.

* The integer type chosen to represent the values of an enumeration type (3.5.2.2).

  * The first integer type in the following list that can represent every value in the enumeration:
    `unsigned char`, `char`, `unsigned short`, `short`, `unsigned int`, `int`

## A.6.3.9 Qualifiers

* What constitutes an access to an object that has volatile-qualified type (3.5.5.3).

  * Any evaluation involving the value of a volatile object constitutes an access.

## A.6.3.10 Declarators

* The maximum number of declarators that may modify an arithmetic, structure, or union type (3.5.4).

  * [Limited only by memory](#Limited-only-by-memory).

## A.6.3.11 Statements

* The maximum number of case values in a switch statement (3.6.4.2).

  * 2^32 (the maximum number of possible values in an expression of integral type)

## A.6.3.12 Preprocessing directives

* Whether the value of a single-character character constant in a constant expression that controls conditional inclusion matches the value of the same character constant in the execution character set. Whether such a character constant may have a negative value (3.8.1).

  * All character constants have the same value in the preprocessor and at
    runtime. No character constants can have negative value.

* The method for locating includable source files (3.8.2).

  * The default search path referred to below is the `include`
    subdirectory of the compiler installation. For example, if the compiler
    was installed to `/usr/local/lcc65`, the default search path is
    `/usr/local/lcc65/include`.

  * Include directives using angle brackets are resolved by searching for the
    given path relative to the default search path.

  * The -I option of the compiler allows the specification of additional
    directories to search for includes. Such directories are searched
    immediately before the default search path, and if more than one is present,
    they are searched from left to right.

* The support of quoted names for includable source files (3.8.2).

  * Include directives using double quotes are resolved by searching relative to
    the directory containing the source file containing the directive. As given
    in the standard, if this fails, the search continues as if the directive had
    been written in angle brackets.

* The mapping of source file character sequences (3.8.2).

  * Source file characters are ASCII, so they are mapped 1-1 to system paths.

* The behavior on each recognized #pragma directive (3.8.6).

  * No `#pragma` directives are defined.

* The definitions for __DATE__ and __TIME__ when respectively, the date and time of translation are not available (3.8.8).

  * The date and time are always available for each host platform the system supports.

## A.6.3.13 Library functions

* The null pointer constant to which the macro NULL expands (4.1.5).

  * `(void*)0`

## Extensions

### Signal Handling

It is well-defined to both read and write a static volatile `sig_atomic_t`
object in a signal handler. (The standard guarantees only writes.)

### Assembly Language Interop

A C program is defined by all C modules visible to the linker. The linker
will produce one assembly output file per section of the linker config. A
higher level will combine these C modules into an assembly file. However,
additional code in this assembly file may need to call or be called by code
outside the program visible to the linker. This section establishes C
language extensions for this purpose.

To call external routines from C, a stub definition of the function should be
created. A stub is marked by calling `__external()` to indicate that it
represents a function defined externally. It does not matter where the stub
is defined, since no code is emitted for it. Calls to the function become
JSRs to the label given by the function name. The calling convention for
arguments and return values is defined below.

To call C from external routines, the function must be marked as externally
visible by calling a builtin function, `__externally_visible()`. This creates
a symbol in the assembler corresponding to the name of the function. The
calling convention is the same that of assembly language routines called from
C.

To allow the compiler to generate efficient code on the 6502, the compiler
makes a great many assumptions about external routines. Particularly, it
assumes that external routines have no visible side effects to processor
registers or the regions of memory reserved to the compiler (via linker
script), except those accessed using volatile. Externally visible C functions
called from external routines do not preserve anything; they may clobber any
memory location made reserved to the compiler, as well as any processor flag
or register. Finally, no C->external->C call chains are assumed possible; all
external routines are assumed to be either roots or leaves of the call graph.

The above assumptions are overly restrictive in many cases, so the compiler
allows external routines to be annotated with their side effects.

In a stub definition, any registers or flags overwritten by the routine can
be marked by calling `__clobbers(<str>)`, where `<str>` is a string
containing one capitalized character per overwritten register or flag. For
example, `__clobbers("NZA")` means that the routine (potentially) overwrits
the N and Z flags and the A register.

In a stub definition, any C routines potentially called by the extrernal routine
can be marked by calling `__calls(<fn>)`. Indicating that a function is called
in this fashion automatically marks the callee as externally visible; that is,
`__externally_visible()` is redundant in the definition of such functions.

#### Calling Convention

The external calling convention uses the A, X, and Y registers to pass
arguments. If there are three or fewer bytes of arguments, then the bytes are
assigned to A, then X, then Y. Otherwise, if the first argument is one byte,
it is still assigned to A. The remaining of the arguments are placed into a
memory region allocated and cleaned up by the caller, and the address of this
memory is placed into X and Y, with X receiving the low byte and Y the high byte.

Note: The compiler uses dynamically optimized calling conventions for C-to-C
calls. The above convention is only used for C-to-external or external-to-C
calls.

### Interrupt Handlers

Given interoperability with ASM, it is possible to write C functions that can
be called in the context of an interrupt handler. Moreover, these calls could
occur while a C function call is active, which requires the compiler to avoid
resource conflicts between the interrupted C functions and the interrupting
ones.

To achieve this, a C function can be marked as being callable inside an
interrupt handler by calling one of a pair of special functions. The two have
slightly different semantics.

`__interrupt()` tells the compiler that the annotated function could be
called while any other C function is active. This does not include the
annotated function itself. It also does not include functions that could only
be called within an activation of the `__interrupt()`-annotated function. Put
another way, the compiler assumes that the function can only be called by an
interrupt if the function is not already active (that is, called, but not yet
returned). This could be achieved by disabling interrupts for the duration or
by using a flag to prevent recursive interrupt handling. The interrupt
handler may already guarantee this, depending on target hardware and OS
features.

Alternatively, `__recursive_interrupt()` tells the compiler that the function
could be called while any C function is active, including itself. Like a
recursive function, this means that resources used by one invocation of the
function necessarily conflict with later invocations. If you can determine
that it is safe to mark a function with `__interrupt()`, do so, since it
improves resource allocation. Otherwise, `__recursive_interrupt()` is always
safe, even if sometimes produces slower code than necessary.