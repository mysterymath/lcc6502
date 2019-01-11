# LCC Bitfield Experiments

This directory contains a number of experiments used to investigate
underspecified aspects of how LCC generates code for bitfields. All results are
produced with the custom frontend configuration found in
[src/bytecode.c](../../src/bytecode.c).

## Experiments

### [types.c](types.c)

This experiment determined whether non-int types could be used with bitfields.

#### Result

No type other than int may be used.

### [min_size.c](min_size.c)

This experiment measures the minimum size of a struct containing a bitfield.

#### Result

A struct containing a bitfield can be as small as one byte. LCC seems to allocate 2 bytes at a time, though.

### [padding.c](padding.c)

This experiment measures whether LCC inserts padding to align integers.

#### Result

No padding is inserted.

### [span.c](span.c)

This experiment measures whether LCC allows bitfields to span storage boundaries.

#### Result

LCC does not allows bit fields to span storage boundaries.

### [zero_width.c](zero_width.c)

This experiment tests the semantics of zero-width bitfields.

#### Result

Zero width bitfields force moving to the next byte, as required by the standard.

### [manip.c](manip.c)

This experiment measures how bit-fields are accessed and mutated, including
their bit order.

#### Result

Bit-fields are allocated least significant bit first within a byte
(little-endian bit order).

Even though sizeof(bf) is 1, bit fields are accessed 2 bytes at a time. Only 1
bit is ever truly modified; the other 15 bits are left alone (given a 1 bit
field). This is (amazingly) standards compliant, even if the other bits are
volatile.Volatile merely means that all accesses and mutations given by the
program occur according to the semantics of the abstract machine, not that the
compiler makes no other accesses or mutations to the objects. (Linus had words
about this).

Code equivalent to the following C is emitted: 
```C
  char s;
  unsigned *s_ptr = (unsigned*)&s;
  *s_ptr |= 1;
  return (*s_ptr << 15) >> 15;
```
