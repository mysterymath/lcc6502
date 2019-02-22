load = $0700
* = load

// Diskette-boot header

// Flags (always zero)
.byt 0

// # of sectors to boot
.byt (end - load + 127)/128

// Load address
.word load

// Init address
.word init

// Boot continuation.
JSR boot
CLC  // Mark boot successful.
RTS

#include "prg_expected.asm"

end = *
disk_end = load + ((end - load + 127)/128) * 128
.dsb disk_end - end,0
