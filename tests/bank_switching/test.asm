// This file contains an assembly language version of the test.
// TODO: Replace appropriate portions of this with C.
// Expected conditions at end of test: A register contains $0A = $1 + $2 + $3 + $4.
// This indicates that all four routines were called in all four banks.

// Bank 0 (always mapped to $B000-$BFFF)
#include "bank0_expected.asm"

bank1_fn:
  BIT $D500 // Select bank 1 (bit 3 = 0, bit 0 = 0)
  JMP bank1_fn_body
bank2_fn:
  BIT $D509 // Select bank 2 (bit 3 = 1, bit 0 = 1)
  JMP bank2_fn_body
bank3_fn:
  BIT $D501 // Select bank 3 (bit 3 = 0, bit 0 = 1)
  JMP bank3_fn_body

// Cartridge header (bank 0, $BFFA-$BFFF)
.dsb $BFFA - *,0
.word start
.byt 0
.byt 4
.word init

#include "bank1_expected.asm"
#include "bank2_expected.asm"
#include "bank3_expected.asm"