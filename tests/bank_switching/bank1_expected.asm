* = $A000

bank1_fn_body:
  CLC
  TAX
  ADC $80
  STA $80
  TXA
  ADC #1
  JMP bank2_fn

.dsb $B000 - *,0
