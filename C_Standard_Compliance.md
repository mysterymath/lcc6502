# C Standard Compliance

For each supported target, the project must conform to the requirements for a
freestanding implementation set forth in the latest [freely-availible
draft](http://port70.net/~nsz/c/c89/c89-draft.html) of ANSI X3.159-1989
"Programming Language C."

Accordingly, all
[implementation-defined behaviors](Implementation_Defined_Behavior.md) must be
documented.

The project must provide functionality sufficient to create a hosted
implementation by writing C libraries. Extensions to the C language may be
provided for this. The requirement to support objects of at least 32767 bytes is
lifted, as the target platforms may not have 32767 contiguous bytes of free RAM.

## Rationale

* C standard compatibility allows running as many libraries as possible without
  modification. Modification may still be required for either non-portable or
  insufficiently performant libraries.
* C89 was the C standard from 1989 to 1999, and is largely backwards-compatible
  with the previous C implementation. Many C libraries are written against it.
* The OS support required for a hosted implementation far exceeds that provided
  by the OS ROM of target platforms. This would require RAM to be used for this,
  even though this functionality may not be required by a specific application.
* A hosted implementation is less useful for target platforms, since they are
  generally programmed more like an embedded system, and less like a POSIX
  computer. Thus, it is left open for one to be developed later as a set of
  libraries.
* The draft is used since the production standard is "generally known" not to
  differ from the draft, and the production standard is difficult to obtain.
  Both technical corrigenda are included, since they provide essential
  corrections to errors in the standard.