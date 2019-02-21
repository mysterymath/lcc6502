// This file contains an assembly language version of the test.
// Expected conditions at end of test: A register contains $0A = $1 + $2 + $3 + $4.
// This indicates that all four routines were called in all four banks, and the
// value was accumulated in a variable initialized from a ROM bank.

// Bank 0 (always mapped to $B000-$BFFF)
#include "bank0_expected.asm"
init:
  RTS
start:
  BIT $D500 // Select bank 1 (bit 3 = 0, bit 0 = 0)
  JSR __bank1_init
  JSR main
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
.dsb $B000 - *,0

#include "bank2_expected.asm"
.dsb $B000 - *,0

#include "bank3_expected.asm"
.dsb $B000 - *,0

