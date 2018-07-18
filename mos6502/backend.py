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
module = parser.parse()

# Compute stack addresses
stack.compute(module)

# DO NOT SUBMIT: Debug print.
module.print()

# Lower operation sizes to single bytes.
for function in module.functions:
    lowerer.lower(function.start)

# Merge basic blocks.
#block_merger.merge(start)

# Select assembly instructions.
#iselector.select(start)

# Emit code to stdout.
#emitter.emit(start)
