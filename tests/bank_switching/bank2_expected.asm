* = $A000

bank2_fn_body:
  CLC
  TAX
  ADC $80
  STA $80
  TXA
  ADC #1
  JMP bank3_fn
