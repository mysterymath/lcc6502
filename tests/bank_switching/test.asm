// This file contains an assembly language version of the test.
// TODO: Replace appropriate portions of this with C.
// Expected conditions at end of test: A register contains $0A = $1 + $2 + $3 + $4.
// This indicates that all four routines were called in all four banks.

// Bank 0 (always mapped to $B000-$BFFF)
* = $B000
init:
  RTS

start:
  LDA #1
  JSR bank1_fn
end:
  JMP end

bank1_fn:
  BIT $D500 // Select bank 1 (bit 3 = 0, bit 0 = 0)
  JMP bank1_fn_body
bank2_fn:
  BIT $D509 // Select bank 2 (bit 3 = 1, bit 0 = 1)
  JMP bank2_fn_body
bank3_fn:
  BIT $D501 // Select bank 3 (bit 3 = 0, bit 0 = 1)
  JMP bank2_fn_body

// Cartridge header (bank 0, $BFFA-$BFFF)
.dsb $BFFA - *,0
.word start
.byt 0
.byt 4
.word init

// Bank 1
* = $A000
bank1_fn_body:
  CLC
  ADC #2
  JMP bank2_fn
.dsb $B000 - *,0

// Bank 2
* = $A000
bank2_fn_body:
  CLC
  ADC #3
  JMP bank3_fn
.dsb $B000 - *,0

// Bank 3
* = $A000
bank3_fn_body:
  CLC
  ADC #4
  RTS
.dsb $B000 - *,0
