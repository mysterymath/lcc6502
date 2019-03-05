PACTL = $D302

load = $0700
* = load

// Cassette-boot header

// Unused byte
.byt 0

// # of 128-byte records to boot
.byt (end - load + 127)/128

// Load address
.word load

// Init address
.word init

// Boot continuation.
JSR boot
CLC
ADC #$FF  // Set carry if return was 1 (indicating error)
RTS

start:
  JSR test
  // NOTE: A reg is set to return value.
loop:
  JMP loop

#echo The C section begins at the below address.
#print *
#include "prg_expected.asm"

end = *
disk_end = load + ((end - load + 127)/128) * 128
.dsb disk_end - end,0
