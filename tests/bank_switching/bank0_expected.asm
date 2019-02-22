* = $B000
init:
  RTS
main:
  LDA #2
  JSR bank1_fn
end:
  JMP end
