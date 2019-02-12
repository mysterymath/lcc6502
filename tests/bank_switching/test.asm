; This file contains an assembly language version of the test.
; TODO: Replace appropriate portions of this with C.

begin = $A000
end = $BFFF

* = begin
init:
RTS
start:
BRK
NOP
RTS
   
.dsb $BFFA - *,0
.word start
.byt 0
.byt 2
.word init

* = begin
.dsb end - *,0