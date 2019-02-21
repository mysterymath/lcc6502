// Diskette-boot header

start = $0700
* = start

// Flags (always zero)
.byt 0

// # of sectors to boot
.byt 1

// Load adderss
.word start

// Init address
.word init

// Multistage load address.
LDA #$A
end:
  JMP end

init:
  LDA #$B
end:
  JMP end
