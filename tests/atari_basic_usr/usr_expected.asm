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
loop:
  BEQ end
  SBC ($CD),Y
  INY
  INY
  DEX
  JMP loop

end:
  RTS
