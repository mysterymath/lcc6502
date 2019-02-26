* = $0600

// Retrieve and save number of arg bytes.
PLA
ASL A  // 2 bytes per arg.
STA $CB

// Call C routine.
JSR usr

// Save return value in BASIC return location.
STA $D4
STX $D5

// Pop args.
TSX
TXA
CLC
ADC $CB
TAX
TXS

// Return to BASIC.
RTS

#echo The C section begins at the below address.
#print *
#include "usr_expected.asm"
