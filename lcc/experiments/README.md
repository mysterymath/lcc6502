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

### [struct_self_ref.c](struct_self_ref.c)

Measures what LCC generates for global structs with self-referential contents.

#### Results

LCC emits a `LABELV <label>` instruction in the `data` section to mark the
start of the structure. It then emits `address <label>` instructions to emit
the address of the struct into the data section.

### [nested_local.c](nested_local.c)

Measures what LCC generates for local variables in nested blocks.

#### Results

LCC hoists all local variables up to function scope. It does not emit any
variable allocation code for block entry or exit (though it does initialize,
as required).

### [omit_return.c](omit_return.c)

Measures what LCC generates when return values are omitted.

#### Results

For long, LCC returns zero instead. For struct types and doubles, LCC
produces an error. This is incorrect; so long as the value of the function
call is not used by the caller, this is well-defined behavior according to
the C89 standard.

### [char_return.c](char_return.c)

Measures what LCC generates when char values are returned.

#### Results

LCC returns an int instead.

### [switch.c](switch.c)

Measures what LCC generates for switch statements.

#### Results

LCC seems to have some intelligence to build binary search branching, but it
looks like we hit a weird corner case. Still, it's not *wrong*, just odd.

See [switch_results.lcc](switch_results.lcc) for details.

### TODO

The following experiments still need to be run:

* Function pointers.
