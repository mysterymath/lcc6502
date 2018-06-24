// EXE magic number.
.word $FFFF

// Note: Free memory: $700 to around $9B00.

start = $0700

.word start
.word end - 1
* = start
lda #$80
sta $4D
loop:
jmp loop
end = *
