* = $0600


// Location to save the end of argument stack, so they can be popped.
ARGS_END = $CB

  TSX
  LDA $100,X  // A = Num Args
  INX

// We need to swap the high and low bytes of each argument here.
// USR stores them big-endian for some unfathomable reason.
// Set the carry bit to count down the arguments to zero.
  SEC

// Skip loop if no arguments.
  BEQ end_swap_loop

swap_loop:
// Save the Xth stack entry
  LDA $100,X
  PHA

// Move the X+1th stack entry to the Xth stack entry
  LDA $100+1,X
  STA $100,X

// Move the saved Xth stack entry to the X+1th entry.
  PLA
  STA $100+1,X

// Advance to the next arg.
  INX
  INX
  SBC #2

// When A reaches zero, the last argument has been reversed.
  BNE swap_loop

end_swap_loop:
  STX ARGS_END
  PLA

// Store ptr to beginning of args in X and Y
  TSX
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

// TODO: Update the .TOML file to incorporate the newly-huge number of bytes this takes.

#echo The C section begins at the below address.
#print *
#include "usr_expected.asm"
