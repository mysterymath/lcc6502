* = $0600

// Retrieve number of args.
PLA

// Call C routine.
JSR usr

// Save return value in BASIC return location.
STA $D4
STX $D5

// Return to BASIC.
RTS

#echo The C section begins at the below address.
#print *
#include "usr_expected.asm"
