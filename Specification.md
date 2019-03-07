# Specification

This document describes the detailed features and charactistics necessary to
achieve the project's requirements. Some specific features (C Implementation
Defined Behavior and Extensions, Linker Scripts, etc) are specified in other
user-facing documents. If so, they are not repeated here.

## Cost Model

There are countless correct implementations of a program that the compiler
could emit. To choose between them, the compiler must establish an ordering
of implementations, from best to worst. As far as is possible, the compiler
should seek to emit the best implementation.

In the absence of other concerns, the compiler should consider
implementations that use fewer clock cycles to those that use more.

When accounting for the number of clock cycles used by an implementation,
clock cycles in a loop should be weighted far more heavily than cycles
outside a loop. For nested loops, the deeper the nesting, the greater the
weight.

Some instructions are more expensive if they cross page boundaries, and
branch instructions are more expensive if the branch is taken. This should be
incorporated into the cycle counts.

In the absence of other concerns, the compiler should prefer implementations
that use fewer bytes of code to those that use more.

When trading off between fewer cycles and fewer bytes of code, the compiler
should prefer to emit as few cycles as possible in the space allotted.

## 6502 Quirks

Due to a number of quirks in the 6502, certain scenarios must be avoided to
avoid bugs. These are listed below.

* A branch instruction can jump at most 127 bytes forward or 128 bytes
  backwards. If a branch needs to travel further, it must branch to an
  absolute jump instead.

* The system must not emit any indirect JMPs through a pointer ending with FF,
  since the NMOS versions of the 6502 have a bug.

* Eight-bit wraparound can occur in two ways, detailed below. Both must be avoided.

  1. Indexed zero page accesses overflow the zero page. This includes uses of the
    `(<ZP>,X)` addressing mode where `<ZP>+X` is greater than 256.

  2. A pair of zero page addresses used as a pointer is dereferenced using either
    the `(,X)` or `(),Y` addressing modes, but the pointer lies on the
    0xFF-0x100 boundary.

* Indexed addressing modes that cross page boundaries (start address + index is
  not at the same 256-byte page as the start address) issue an erroneous read
  from the old page, exactly 256 bytes prior to the correct address. The
  compiler must ensure that only addresses reserved for use by the compiler are
  accessed in such a way.

* The compiler must not use the read-modify-write instructions INC or DEC with
    volatile types.

* The BRK instruction should not be used by the compiler, due to a bug in
  interrupt handling.