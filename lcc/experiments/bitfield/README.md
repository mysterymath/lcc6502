# LCC Bitfield Experiments

This directory contains a number of experiments used to investigate
underspecified aspects of how LCC generates code for bitfields. A brief summary of
each experiment is given below. All results are produced with the custom frontend
configuration found in [src/bytecode.c](../../src/bytecode.c).

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
