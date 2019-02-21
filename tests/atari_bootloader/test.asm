// Test flow:
// Continuation handler runs.
// Set MEMLO and APPHI to highest used address.
// Set DOSVEC to loader.
// Init runs, RTS.
// loader runs, loads $A to A reg and hangs.
// Verify that A is in A reg.
// Soft reset.
// Verify that A is in A reg.

start = $0700
* = start

DOSVEC = $A
APPMHI = $E
MEMLO = $2E7

// Diskette-boot header

// Flags (always zero)
.byt 0

// # of sectors to boot
.byt 1

// Load address
.word start

// Init address
.word init

// Multistage load address.
  LDA #<loader
  STA DOSVEC
  LDA #>loader
  STA DOSVEC+1
  LDA #<free
  STA MEMLO
  STA APPMHI
  LDA #>free
  STA MEMLO+1
  STA APPMHI+1
  CLC  // Mark boot successful.
  RTS

init:
  RTS

loader:
  LDA #$A
end:
  JMP end

free = *

.dsb 128-(* - start),0
