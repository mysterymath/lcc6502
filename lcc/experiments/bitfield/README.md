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

A struct containing a bitfield can be as small as one byte.

### [padding.c](padding.c)

This experiment measures whether LCC inserts padding to align integers.

#### Result

No padding is inserted.

### [span.c](span.c)

This experiment measures whether LCC allows bitfields to span byte boundaries.

#### Result

LCC allows bit fields to span byte boundaries.

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

It seems even though sizeof(bf) is 1, it promotes an automatic variable of that
type to an int (2 bytes).

Code effectively equivalent to the following C is emitted: int s; s |= 1; return
(s << 15) >> 15;