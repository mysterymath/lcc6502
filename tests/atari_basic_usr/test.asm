// Retrieve number of args.
PLA

// Call C routine.
JSR usr

// Save return value in BASIC return location.
STA $D4
STX $D5

// Return to BASIC.
RTS

