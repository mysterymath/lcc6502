DOSVEC = $A
APPMHI = $E
MEMLO = $2E7

init:
  RTS

start:
  LDA #$A
loop:
  JMP loop

boot:
  LDA #<start
  STA DOSVEC
  LDA #>start
  STA DOSVEC+1
  LDA #<end
  STA MEMLO
  STA APPMHI
  LDA #>end
  STA MEMLO+1
  STA APPMHI+1
  RTS

