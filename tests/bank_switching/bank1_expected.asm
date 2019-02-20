* = $A000

__bank1_init:
  LDA #1
  STA $80
  RTS

bank1_fn_body:
  CLC
  TAX
  ADC $80
  STA $80
  TXA
  ADC #1
  JMP bank2_fn