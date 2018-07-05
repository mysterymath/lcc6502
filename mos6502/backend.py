import attr
import re
import sys
from attr import attrs, attrib
from yapf.yapflib.yapf_api import FormatCode

def read():
    global line
    line = sys.stdin.readline().strip()

def expect(expected):
    global line
    assert line == expected, "Expected: '{}'. Actual: '{}'".format(expected, line);
    read()

read()
expect("export main")
expect("code")
expect("proc main 0 0")

@attrs
class Store(object):
    address = attrib()
    value = attrib()

@attrs
class Jump(object):
    destination = attrib()

@attrs(cmp=False)
class BasicBlock(object):
    instructions = attrib()

    @property
    def terminator(self):
        return self.instructions[-1]

labels = {}
instructions = []
block = BasicBlock(instructions)
start = block
while line != "endproc main 0 0":
    if not line:
        raise "Expected: 'endproc main 0 0'. Found: EOF"
    components = line.split()
    match = re.match("(\w+)(\D)(\d)?", components[0])
    operation = match[1]
    #instruction = Instruction(match[1], match[2], match[3] and int(match[3]))

    if operation == 'CNST':
        instructions.append(int(components[1]))
    elif operation == 'ASGN':
        value = instructions.pop()
        address = instructions.pop()
        instructions.append(Store(address, value))
    elif operation == 'LABEL':
        label = components[1]
        if label in labels:
            block = labels[block]
        else:
            block = BasicBlock([])
            labels[label] = block
        instructions.append(Jump(block))
        instructions = block.instructions
    elif operation == 'ADDRG':
        label = components[1]
        if label not in labels:
            labels[label] = BasicBlock([])
        instructions.append(labels[label])
    elif operation == 'JUMP':
        destination = instructions.pop()
        instructions.append(Jump(destination))
        block = BasicBlock([])
        instructions = block.instructions

    read()

def pprint(x):
    print(FormatCode(repr(x))[0], end='')


# Generate code for each basic block, from start to end.

block_ids = {}

block = start
while True:
    # Generate a label for each block.
    if block not in block_ids:
        block_ids[block] = len(block_ids)
    print(".{}:".format(block_ids[block]))

    # TODO: Generate instructions (except terminator).
    for instruction in block.instructions[:-1]:
        pprint(instruction)

    # Jump is currently the only supported block terminator.
    assert isinstance(block.terminator, Jump)

    # Jumps to already-generated blocks must be emitted.
    if block.terminator.destination in block_ids:
        print("JMP .{}".format(block_ids[block.terminator.destination]))
        # Since all jumps are currently unconditional, the first backward jump starts an infinite loop.
        # This means we are done.
        break
    else:
        # Jumps to not-yet-generated blocks can be handled using fall-through.
        # This requires generating the destination next.
        block = block.terminator.destination
