* = $0600


// Location to save the end of argument stack, so they can be popped.
ARGS_END = $CB

  TSX
  INX
  LDY $100,X  // A = Num Args, Z = A == 0

// We need to swap the high and low bytes of each argument here.
// USR stores them big-endian for some unfathomable reason.

// Throughout the loop, the X register is maintained as the top of the
// unprocessed stack. At the end of the loop, X will contain the top of the
// stack if all the arguments were popped.

// Skip loop if no arguments.
  BEQ end_swap_loop

swap_loop:
// Save the Xth stack entry
  LDA $100+1,X
  PHA

// Move the X+1th stack entry to the Xth stack entry
  LDA $100+2,X
  STA $100+1,X

// Move the saved Xth stack entry to the X+1th entry.
  PLA
  STA $100+2,X

// Advance to the next arg.
  INX
  INX
  DEY

// When A reaches zero, the last argument has been reversed.
  BNE swap_loop

end_swap_loop:
  STX ARGS_END
  PLA

// Store ptr to beginning of args in X and Y
  TSX
  INX
  LDY #$01

// Call C routine.
  JSR usr

// Save return value in BASIC return location.
  STA $D4
  STX $D5

// Pop args.
  LDX ARGS_END
  TXS

// Return to BASIC.
  RTS

#echo The C section begins at the below address.
#print *
#include "usr_expected.asm"
