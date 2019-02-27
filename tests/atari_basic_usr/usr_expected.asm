* = $062C
usr:
  STX $CC
  STY $CD
  TAX
  LDY #0

  LDA ($CC),Y
  INY
  INY
  DEX

  SEC
  BEQ end
loop:
  SBC ($CC),Y
  INY
  INY
  DEX
  BNE loop

end:
  RTS
