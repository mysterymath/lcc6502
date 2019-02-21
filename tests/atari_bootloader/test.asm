// Test flow:
// Continuation handler runs.
// Set MEMLO and APPHI to highest used address.
// Set DOSVEC to loader.
// Init runs, RTS.
// loader runs, loads $A to A reg and hangs.
// Verify that A is in A reg.
// Soft reset.
// Verify that A is in A reg.

load = $0700
* = load
sector1 = *

DOSVEC = $A
APPMHI = $E
MEMLO = $2E7

DUNIT = $0301
DCOMND = $0302
DBUF = $0304
DAUX1 = $030A
DAUX2 = $030B

DSKINV = $E453

// Diskette-boot header

// Flags (always zero)
.byt 0

// # of sectors to boot
.byt 1

// Load address
.word load

// Init address
.word init

// Multistage loader.
  LDA #1
  STA DUNIT

  LDA #$52
  STA DCOMND

  LDA #<sector2
  STA DBUF
  LDA #>sector2
  STA DBUF+1

  LDA #2
  STA DAUX1
  LDA #0
  STA DAUX2

  JSR DSKINV

  LDA #<start
  STA DOSVEC
  LDA #>start
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

.dsb 128-(* - sector1),0

* = $900
sector2 = *
start:
  LDA #$A
end:
  JMP end

free = *
.dsb 128-(* - sector2),0
