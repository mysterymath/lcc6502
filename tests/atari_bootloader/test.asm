
start = $0700
* = start

// Diskette-boot header

// Flags (always zero)
.byt 0

// # of sectors to boot
.byt 1

// Load adderss
.word start

// Init address
.word init

// Multistage load address.
// TODO: Update MEMLO and APPMHI to first free address.
// TODO: Set DOSVEC to start entry of application.
CLC  // Mark boot successful.
RTS

init:
  LDA #$B
end2:
  JMP end2

.dsb 128-(* - start),0
