* = $B000
init:
  RTS

start:
  LDA #1
  JSR bank1_fn
end:
  JMP end
