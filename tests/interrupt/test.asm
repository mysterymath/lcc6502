// This file produces the final cartridge image for the test.

* = $A000

init:
  RTS

start:
  BRK
  NOP
loop:
  JMP loop

// Cartridge header (bank 0, $BFFA-$BFFF)
.dsb $BFFA - *,0
.word start
.byt 0
.byt 4
.word init
