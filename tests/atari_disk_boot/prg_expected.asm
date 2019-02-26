* = $0713
boot:
  LDA #<start
  STA $A
  LDA #>start
  STA $B
  LDA #<end
  STA $E
  STA $2E7
  LDA #>end
  STA $F
  STA $2E8
  LDA #0
  RTS

init:
  RTS

test:
  LDA #$A
  RTS
