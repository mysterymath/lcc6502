begin = $A000
end = $BFFF

* = begin
init:
BRK
NOP
RTS
start:
BRK
NOP
RTS
   
.dsb $BFFA - *,0
.word start
.byt 0
.byt 1
.word init
