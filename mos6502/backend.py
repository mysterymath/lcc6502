from attr import attrs, attrib
from yapf.yapflib.yapf_api import FormatCode

import asm
import block_merger
import emitter
import inliner
import ir
import iselector
import lowerer
import parser
import stack


def pprint(x):
    print(FormatCode(repr(x))[0], end='')


# Parse LCC bytecode into function IR.
functions = parser.parse()

# Compute stack addresses
for function in functions:
    stack.compute(function.start)

# Lower operation sizes to single bytes.
for function in functions:
    lowerer.lower(function.start)

# DO NOT SUBMIT: Debug print.
for function in functions:
    print(function.name + ":")
    ir.print_blocks(function.start)

# Inline leaf functions until none remain.
#inliner.inline(functions)
#start = [f for f in functions if f.name == 'main'][0].start

# Merge basic blocks.
#block_merger.merge(start)


# Select assembly instructions.
#iselector.select(start)

# Emit code to stdout.
#emitter.emit(start)
