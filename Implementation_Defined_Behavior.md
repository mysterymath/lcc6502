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
* For the Atari 800 the execution character set is ATASCII.
  * ASCII '{' is mapped to inverse '['.
  * ASCII '}' is mapped to inverse ']'.
  * ASCII '~' is mapped to inverse '-'.
  * ASCII vertical tab is mapped (somewhat arbitrarily) to "Cursor Down".
  * ASCII form feed is mapped to "Clear Screen".
  * ASCII alert is mapped to "Buzzer".
  * ASCII carriage return is mapped (somewhat arbitrarily) to "Cursor Left".
  * All other members of the basic character set take their natural mappings.
  * An alternative mapping is provided for the internal ROM character mapping.
* For the Commodore 64 the execution character set is PETSCII.
  * ASCII '^' is mapped to up arrow.
  * ASCII '\' is mapped to the British pound sign.
  * ASCII '|' is mapped to $DD.
  * ASCII '~' is mapped to $B2.
  * ASCII '{' is mapped to $EB.
  * ASCII '}' is mapped to $F3.
  * ASCII tab is mapped (somewhat arbitrarily) to "Cursor Right".
  * ASCII vertical tab is mapped (somewhat arbitrarily) to "Cursor Down".
  * ASCII form feed is mapped to "Clear Screen".
  * ASCII carriage return is mapped (somewhat arbitrarily) to "Cursor Left".
  * ASCII alert is mapped (arbitrarily) to $01 (unused by PETSCII).
  * An alternative mapping is provided for the internal ROM character mapping.
* TODO: Define the extension mechanism for custom character mappings and
  non-null-terminated string literals.

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
  then converted to the target type.
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