__jmp = $1
__retv = $10

// TODO: How does C library code like longjmp get placed in sections.
// TODO: How does this interact w bank switching?
// TODO: The C stack (if any)? What if there is none?
// TODO: What sort of calling convention is this? How are setjmp and longjmp
// implemented in C? It's a mix of C and assembly, so we shouldn't need any
// magic. And if so, how do we reserve zero page addresses for these routines.
// Hmm...

outer:
  // TODO
  NOP

inner:
  // TODO
  NOP

setjmp:
  PHP
  TYA
  PHA

  // No need to save A or X, since these will be the return values.

  // Save return address
  TSX
  LDA $101,X
  LDY #reta
  STA (__jmp),Y
  LDA $102,X
  INY
  STA (__jmp),Y

  // Save Y
  PLA
  LDY #y
  STA (__jmp),Y

  // Save P
  PLA
  LDY #p
  STA (__jmp),Y
  
  // Return 0
  LDA #0
  LDX #0
  RTS

longjmp:
  // On entry, A and X contain RetV.
  // Save A. X will remain set.
  STA __retv

  // Push return address (High byte first, so the data is stored little-endian)
  LDY #reta+1
  LDA (__jmp),Y
  PHA
  DEY
  LDA (__jmp),Y
  PHA

  // Push P
  LDA #p
  LDA (__jmp),Y
  PHA

  // Restore Y
  LDY #y
  LDA (__jmp),Y
  TAY

  // Set A to the return value. X remains set.
  LDA __retv

  // Restore P
  PLP

  // Perform the long jump
  RTS