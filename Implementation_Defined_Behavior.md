# Implementation-Defined Behavior

The C89 standard requires a conforming implementation to document a number of
"implementation-defined" behaviors and characteristics. All such behaviors
and characteristics are defined here. This document is organized in
parallel to the standard, section for section.

1.6 [DEFINITIONS OF TERMS](http://port70.net/~nsz/c/c89/c89-draft.html#1.)

* A byte contains 8 bits.
* These platforms have no alignment requirements. No padding is used.
* An short consists of 2 little-endian bytes.
* An int consists of 2 little-endian bytes.
* A long consists of 4 little-endian bytes.
* A float consists of 4 bytes encoded using the IEEE 754 binary32 format.
* A double consists of 8 bytes encoded using the IEEE 754 binary64 format.
* TODO: When selecting a soft float lib, verify that it uses the above formats.
* Structures elements are laid out sequentially in memory in declaration order,
  without padding.

2.1.2.1 [Freestanding
environment](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.2.1.)

* TODO: Define any additional library routines provided by this implementation.

* All external identifiers that begin with an underscore are reserved. All other
  identifiers that begin with an underscore and either an upper-case letter or
  another underscore are reserved. If the program defines an external identifier
  with the same name as a reserved external identifier, even in a semantically
  equivalent form, the behavior is undefined.

2.1.2.3 [Program execution](https://port70.net/~nsz/c/c89/c89-draft.html#2.1.2.3.)

* This implementation defines no interactive devices.

2.2.1 [Character sets](https://port70.net/~nsz/c/c89/c89-draft.html#2.2.1)

* The source character set is ASCII for all targets.
* For the Atari 800 the execution character set is ATASCII, minus the heart
  character present at zero.
* For the Commodore 64 the execution character set is shifted PETSCII.

3.1.2 [Identifiers](https://port70.net/~nsz/c/c89/c89-draft.html#3.1.2)

* Number of significant characters in an internal identifier: limited only by
  available memory.
* Number of significant characters in an external identifier: limited only by
  available memory.
* External identifiers are case-sensitive.

3.1.2.5 [Types](https://port70.net/~nsz/c/c89/c89-draft.html#3.1.2.5)

* Chars are defined to be unsigned, since target platform has useful
  characters with the high bit set, and all values of characters must be
  positive.

3.1.3.4 [Character constants](https://port70.net/~nsz/c/c89/c89-draft.html#3.1.3.4)

* The preprocessor and compiler both map character literals to the values that
  they have on the target machine.

* For the Atari 800 characters are mapped naturally, except the following:
  * ASCII '{' is mapped to inverse '['.
  * ASCII '}' is mapped to inverse ']'.
  * ASCII '~' is mapped to inverse '-'.
  * ASCII vertical tab is mapped (somewhat arbitrarily) to "Cursor Down".
  * ASCII form feed is mapped to "Clear Screen".
  * ASCII alert is mapped to "Buzzer".
  * ASCII carriage return is mapped (somewhat arbitrarily) to "Cursor Left".
* For the Commodore 64 characters are mapped naturally, except the following:
  * ASCII '^' is mapped to up arrow.
  * ASCII '\' is mapped to the British pound sign.
  * ASCII '|' is mapped to $7D.
  * ASCII '~' is mapped to $AE.
  * ASCII '{' is mapped to $AB.
  * ASCII '}' is mapped to $B3.
  * ASCII tab is mapped (somewhat arbitrarily) to "Cursor Right".
  * ASCII vertical tab is mapped (somewhat arbitrarily) to "Cursor Down".
  * ASCII form feed is mapped to "Clear Screen".
  * ASCII carriage return is mapped (somewhat arbitrarily) to "Cursor Left".
  * ASCII alert is mapped (arbitrarily) to $01 (unused by PETSCII).
 
3.2.1.2 [Signed and unsigned integers](https://port70.net/~nsz/c/c89/c89-draft.html#3.2.1.2)

* When an integer is converted to a signed integral type that cannot represent
  its value, the bytes of the source integer are reinterpreted as those of the
  target type. If the target type is smaller, only the lower-order byte(s) are
  considered.

3.2.1.3 [Floating and integral](https://port70.net/~nsz/c/c89/c89-draft.html#3.2.1.3)

* TODO: Determine whether converting from int to float rounds up or down (or
  both in some complex way).

3.2.1.4 [Floating types](https://port70.net/~nsz/c/c89/c89-draft.html#3.2.1.4)

* TODO: Determine whether converting from floating type to smaller floating
  type rounds up or down (or both in some complex way).

3.3.2.3 [Expressions](https://port70.net/~nsz/c/c89/c89-draft.html#3.3)

* Bitwise operators on signed types produce the result of first converting to
  the corresponding unsigned type, then applying the operator, then converting
  back to the corresponding signed type.

3.3.2.3 [Structure and union members](https://port70.net/~nsz/c/c89/c89-draft.html#3.3.2.3)

* If a member of a union object is read after a value has been stored in a
  different member of the object, the bytes of the value are reinterpreted as
  the new type. If they do not represent a value in the new type, the behavior
  is undefined.

3.3.3.4 [The sizeof operator](https://port70.net/~nsz/c/c89/c89-draft.html#3.3.3.4)

* See section 1.6 for the layout of objects. The behavior of sizeof trivially
  follows.

3.3.4 [Cast operators](https://port70.net/~nsz/c/c89/c89-draft.html#3.3.4)

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

3.3.5 [Multiplicative operators](https://port70.net/~nsz/c/c89/c89-draft.html#3.3.5)

* When exactly one of the operators to the ```/``` operator is negative, the
  result is the smallest integer greater than the algebraic quotient. This
  "round towards zero" behavior mimics FORTRAN and the later C99 standard.
* The result of the ```%``` operator is such that ```(a/b)*b + a%b``` equals
   ```a``` whenever ```a/b``` is representable.

3.3.6 [Additive operators](https://port70.net/~nsz/c/c89/c89-draft.html#3.3.6)

* The size of the result of subtracting two pointers is 2 bytes.

3.3.7 [Bitwise shift operators](https://port70.net/~nsz/c/c89/c89-draft.html#3.3.7)

* Right shifts of signed values are arithmetic, not logical. That is, the sign bit
  is copied to fill in the empty space left by shifting the other bits right. Though
  this is not required by the C89 standard, and though it is slower on the 6502 than
  logical shifts, breaking convention with nearly every other C implementation would
  burden portability of existing C code.

3.5.1 [Storage-class specifiers](https://port70.net/~nsz/c/c89/c89-draft.html#3.5.1)

* The `register` storage class has no effect on the output of the compiler
  beyond that mandated by the standard.

3.5.2.1 [Struct and union specifiers](https://port70.net/~nsz/c/c89/c89-draft.html#3.5.2.1)

* The high-order bit of a "plain" `int` bitfield is treated as a sign bit.
* Since the 6502 has no alignment requirements, space is allocated one byte at
  a time.
* If insufficient space remains in a byte for a bit field, the bit field is
  allocated to the beginning of the next byte.
* Following the convention of little-endian machines like the 6502, bit fields
  are allocated from low-order bits to high-order bits within a byte.

3.5.2.2 [Enumeration specifiers](https://port70.net/~nsz/c/c89/c89-draft.html#3.5.2.2)

* An enumerated type is compatible with the first integer type in the following
  list that can represent every value in the enumeration:
  unsigned char, char, unsigned short, short, unsigned int, int

3.5.3 [Type qualifiers](https://port70.net/~nsz/c/c89/c89-draft.html#3.5.3)

* Any evaluation involving the value of a volatile object constitutes an access.
* Reads/writes to volatile objects are only guaranteed to be atomic if one
  byte is accessed.

3.8.2 [Source file inclusion](https://port70.net/~nsz/c/c89/c89-draft.html#3.8.2)

* The default search path referred to below is the section of the `include`
  subdirectory of the compiler installation with the same name as the target
  specification. For example, if the compiler was installed to
  `/usr/local/lcc65`, and the target is `c64`, the default search path is
  `/usr/local/lcc65/include/c64`.

* Include directives using angle brackets are resolved by searching for the
  given path relative to the default search path.

* Include directives using double quotes are resolved by searching relative to
  the directory containing the source file containing the directive. As given
  in the standard, if this fails, the search continues as if the directive had
  been written in angle brackets.

* The -I option of the compiler allows the specification of additional
  directories to search for includes. Such directories are searched
  immediately before the default search path, and if more than one is present,
  they are searched from left to right.

3.8.6 [Pragma directive](https://port70.net/~nsz/c/c89/c89-draft.html#3.8.6)

* TODO: Define the syntax and semantics of any `#pragma` directives.

4.7 [SIGNAL HANDLING](https://port70.net/~nsz/c/c89/c89-draft.html#4.7)

* Only one byte can be read or written in one instruction (atomically).
  Equivalently, `sig_atomic_t` would be defined as `char`, even though no
  `<signal.h>` implementation is provided.

* A function annotation should be provided to mark a function as an interrupt
  handler. This alters the generation of the function such that:
  * `RTI` is issued for each return instead of `RTS`.
  * Any resources used by the function or any of its descendants must be saved
    on entry and restored on exit, since the interrupted function cannot know
    that it needs to save them.

* TODO: Define the syntax of the interrupt annotation.