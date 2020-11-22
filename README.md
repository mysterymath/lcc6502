# LCC 6502 C Compiler

This project was to create a modern C compiler for the MOS 6502.

## Project Status

This project has been significantly reconceived. I took another stab at getting
this to work in LLVM, and turns out I just had to bash my head hard enough
against that codebase for it to start making sense. It looks like most of the pieces
I need for this project are already in LLVM (big surprise), it's just a matter of
fitting them all together and adding the remaining bits. As such, the LCC version of
this is now dead.

I'll no longer be implementing my own linker, so most of that is dead too.
Instead, I'm piggybacking on the cc65 assembler and linker ecosystem. The rest
of cc65 is perfectly fine; the compiler just could use a tune up.

Updated November 21, 2020.
