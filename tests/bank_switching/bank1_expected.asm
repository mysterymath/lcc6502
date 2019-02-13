* = $A000

bank1_fn_body:
  CLC
  ADC #2
  JMP bank2_fn

.dsb $B000 - *,0
