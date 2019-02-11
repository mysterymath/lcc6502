# Design Rationale

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

* Reducing bit-field strength improves performances and prevents a confusing
   corner case where writes to bit-fields may overwrite asynchronous changes
   to neighboring structure fields, even those declared volatile. This
   behavior is allowed by the standard, but many people find it surprising.

* The BRK instruction can be swallowed in NMOS chips if a hardware interrupt
   occurs while one is being fetched. This was corrected in the CMOS
   implementation. To avoid this complexity, and due to insufficient utility, the
   BRK instruction should not be used.

* Prototypes in library headers may only use identifiers in the reserved
    namespace (`__x` or `_X`). Otherwise, the user could place a #define macro
    before the header as follows:

```C
#define status []
void exit(int status);
```

This becomes:

```C
void exit(int []);
```