* = $A000

bank2_fn_body:
  CLC
  ADC #3
  JMP bank3_fn

.dsb $B000 - *,0
