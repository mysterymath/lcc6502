# C Standard Compliance

For each supported target, the project must conform to the requirements for a
hosted implementation set forth in the latest [freely-availible
draft](http://port70.net/~nsz/c/c89/c89-draft.html) of ANSI X3.159-1989
"Programming Language C."

## Rationale

* C standard compatibility allows running as many libraries as possible without
  modification. Modification may still be required for either non-portable or
  insufficiently performant libraries.
* ANSI C was the C standard from 1989 to 1999, and is largely
  backwards-compatible with the previous C implementation. Many C libraries are
  written against it.
* The project must supply hosted implementations of the language (see the C
  standard). This allows programs to be written that feel more like writing on a
  personal computer, and less like writing on a microcontroller. These platforms
  largely do have operating systems already, and these OS routines can be
  leveraged to create native hosted implementations.
* The next version of the C standard, C99, requires that hosted implementations
  support "65535 bytes in an object." This precludes creating a hosted
  implementation for C99 on the 6502, which can address at most 65536 bytes.
  Such an object would take up the entire addressible memory space.
* The draft is used since the production standard is "generally known" not to
  differ from the draft, and the production standard is difficult to obtain. No
  technical corrigenda need be considered, since these were not availible at the
  time of drafting.
