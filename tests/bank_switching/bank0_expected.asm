* = $B000
init:
  RTS

start:
  LDA #2
  JSR bank1_fn
end:
  JMP end
