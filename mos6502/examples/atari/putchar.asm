// EXE magic number.
.word $FFFF

// Note: Free memory: $700 to around $9B00.

start = $0700

CIOV = $E456
IOCB0 = $0340
ICCMD = 2
ICBLL = 8
ICBLH = 9

PUT_CHARACTERS = $0B

.word start
.word end - 1
* = start
lda #PUT_CHARACTERS
sta IOCB0+ICCMD
lda #0
sta ICBLL
sta ICBLH
lda #"A"
ldx #0
jsr CIOV
loop:
jmp loop
end = *
