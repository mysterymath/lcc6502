# Specification Rationale

## 6502 Quirks

All quirky situations are best avoided, since they are easy to detect, and
not really required to emit fast code. This is especially true for NMOS vs
CMOS differences, since it allows the compiler to emit code that works on
both CPUs.

Erroneous reads caused by indexed page crossings could trigger undesirable
behavior if they access I/O registers that perform actions on reads. To avoid
creating a class of particularly nasty bugs, the compiler must ensure that if
such spurious reads occur, they touch only memory declared to be safe for
compiler purposes.

On the NMOS 6502, INC and DEC issue two writes: first the unmodified data,
then the modified data. CMOS versions instead issue two reads, but only one
write. Even though it is permissible by the standard, the compiler should not
use these instructions for volatile types, since the behavior is quite
surprising and is not necessary. It may cause issues with interrupts or
system registers.
