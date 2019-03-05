// foo is called in a non-recursive interrupt handler, so $80 can be reserved
// for it.
// Note: If non-recursive interrupt handlers would take too many resources, the
// optimizer can always use the stack like a recursive handler. That's always an
// option, but more, usually cheaper options are available for nonrecursive
// interrupts.
__foo:
  STA $80
  TXA
  CLC
  ADC $80
  RTS

// Recursive interrupt handlers can be interrupted by the same interrupt that
// called the handler. This means that any resource used by the handler is
// potentially in conflict with future calls, just as in a recursive function.
// Accordingly, the hard stack is used here instead of a (normally) faster ZP
// address, since saving the ZP address before using it is slower than just
// using the stack.
__bar:
  PHA
  TXA
  TSX
  INX
  CLC
  ADC $100,X
  TXS
  RTS

// baz might be interrupted by foo, so it cannot use $80.
baz:
  STA $81
  TXA
  CLC
  ADC $81
  RTS

nonrecursive:
  JMP __foo

recursive:
  JMP __bar
