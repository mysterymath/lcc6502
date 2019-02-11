# Requirements Rationale

This document gives the rationale for the [Requirements.md](requirements). It
is organized in parallel with the requirements document, section for section.

## Execution Environments

* 8KB are the simplest type of cartridge. OSS one-chip 16 KB cartridges also
   need to be supported to ensure that it is possible to write programs where
   code is bank-switched in and out.

* Casettes are very similar to disk in their requirements, so a quick check
   that they are supported at all should roughly ensure similar capabilities to
   disk.