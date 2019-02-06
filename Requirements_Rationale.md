# Requirements

This document gives the rationale for the [Requirements.md](requirements). It
is organized in parallel with the requirements document, section for section.

* 8KB are the simplest type of cartridge. OSS one-chip 16 KB cartridges also
   need to be supported to ensure that it is possible to write programs where
   code is bank-switched in and out.

* Casettes are very similar to disk in their requirements, so a quick check
   that they are supported at all should roughly ensure similar capabilities to
   disk.

* Target systems have a huge number of RAM and ROM configurations, and porting
   to other systems requires even more. It would be difficult to impossible to
   support them all directly, so an abstraction mechanism is needed. Logically,
   the compiler can produce code in any address configuration at all; if a
   configuration mechanism is provided for this, then any plausible
   configuration can be used. It would then fall to support routines to
   initialize the system such that those resources are indeed free, then to give
   control to the C program. These routines can also be written in C by writing
   them as a separate program with a smaller execution environment. The two
   programs would then be linked together by the assembler.

## Design

* Erroneous reads could trigger undesirable behavior if they access I/O
   registers that perform actions on reads. To avoid creating a class of
   particularly nasty bugs, the compiler must ensure that if such spurious reads
   occur, they touch only memory declared to be safe for compiler purposes.

* Read-modify-write instructions like INC first write the unmodified data, then
   the modified data. CMOS versions instead issue two reads, but only one
   write. Even though it is permissible by the standard, the compiler should
   not use these instructions for volatile types, since the behavior is quite
   surprising and is not necessary. It may cause issues with interrupts or
   system registers.

* The expectation is that objects accessed using `volatile` can be modified
   outside the program, so it doesn't make sense to put them in ROM, even if
   the C compiler never observes changes.