* = $0609
usr:
  TAY

  TSX
  INX
  INX
  LDA $100,X
  INX
  INX
  DEY

  SEC
loop:
  BEQ end
  SBC $100,X
  INX
  INX
  DEY

end:
  RTS
