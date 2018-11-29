# C Standard Compliance

For each supported target, the project must conform to the requirements for a
freestanding implementation set forth in the latest [freely-availible
draft](http://port70.net/~nsz/c/c89/c89-draft.html) of ANSI X3.159-1989
"Programming Language C."

## Rationale

* C standard compatibility allows running as many libraries as possible without
  modification. Modification may still be required for either non-portable or
  insufficiently performant libraries.
* C89 was the C standard from 1989 to 1999, and is largely backwards-compatible
  with the previous C implementation. Many C libraries are written against it.
* The project supplies freestanding implementations of the language (see the C
  standard). The hosted implementation places expectations on the OS; these are
  frequently not met by the target platforms.
* The project must provide functionality sufficient to create a (mostly) hosted
  implementation by writing C libraries. Extensions to the C language may be
  provided for this.
  * Deviations from standard hosted implementation:
    * The requirement to support objects of at least 32767 bytes is lifted, as
      the target platforms can only address 65536 bytes.
* The next version of the C standard, C99, requires that hosted implementations
  support "65535 bytes in an object." This precludes creating a hosted
  implementation for C99 on the 6502, which can address at most 65537 bytes.
  Such an object would take up the entire addressible memory space.
* The draft is used since the production standard is "generally known" not to
  differ from the draft, and the production standard is difficult to obtain.
  Both technical corrigenda are included, since they provide essential
  corrections to errors in the standard.
