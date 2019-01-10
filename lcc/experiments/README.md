# LCC Experiments

This directory contains a number of experiments used to investigate
underspecified aspects of LCC's code generation interface. A brief summary of
each set of experiments is given below.

## Experiments

### [bitfield](bitfield/)

Measures what LCC generates for struct bitfield accesses and mutations.

### [struct_init.c](struct_init.c)

Measures what LCC generates for automatic struct variable initialization.

#### Results

LCC performs struct initialization much like character array initialization.
Space for the initializer is statically allocated, and an assignment is issued
at the beginning of the block from the static location to the variable. LCC does
not combine identical initializers; instead, it creates one initializer per struct
literal instance in the source text.