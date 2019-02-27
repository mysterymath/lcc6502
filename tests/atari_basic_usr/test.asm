* = $0600

// Retrieve and save number of args.
PLA
STA $CB

// Store ptr to beginning of args in X and Y
TSX
LDY #$01

// Call C routine.
JSR usr

// Save return value in BASIC return location.
STA $D4
STX $D5

// Pop args.
TSX
TXA
CLC
// Each arg is two bytes.
ADC $CB
ADC $CB
TAX
TXS

// Return to BASIC.
RTS

#echo The C section begins at the below address.
#print *
#include "usr_expected.asm"
