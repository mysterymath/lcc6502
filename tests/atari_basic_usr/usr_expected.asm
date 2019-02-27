* = $0617
usr:
  STX $CC
  STY $CD
  TAX
  LDY #0

  LDA ($CD),Y
  INY
  INY
  DEX

  SEC
  BEQ end
loop:
  SBC ($CD),Y
  INY
  INY
  DEX
  BNE loop

end:
  RTS
