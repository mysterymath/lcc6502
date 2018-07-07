from attr import attrs, attrib
from yapf.yapflib.yapf_api import FormatCode

import asm
import emitter
import inliner
import ir
import iselector
import lowerer
import parser


def pprint(x):
    print(FormatCode(repr(x))[0], end='')


# Parse LCC bytecode into function IR.
functions = parser.parse()

# Inline leaf functions until none remain.
inliner.inline(functions)

start = [f for f in functions if f.name == 'main'][0].start

# Lower operation sizes to single bytes.
lowerer.lower(start)

# Select assembly instructions.
iselector.select(start)

# Emit code to stdout.
emitter.emit(start)
