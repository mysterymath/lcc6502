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
    addr = attrib()
    value = attrib()

@attrs
class Jump(object):
    dest = attrib()

@attrs
class BasicBlock(object):
    instructions = attrib()

labels = {}
instructions = []
block = BasicBlock(instructions)
start = block
while line != "endproc main 0 0":
    if not line:
        raise "Expected: 'endproc main 0 0'. Found: EOF"
    components = line.split()
    match = re.match("(\w+)(\D)(\d)?", components[0])
    op = match[1]
    #instruction = Instruction(match[1], match[2], match[3] and int(match[3]))

    if op == 'CNST':
        instructions.append(int(components[1]))
    elif op == 'ASGN':
        value = instructions.pop()
        addr = instructions.pop()
        instructions.append(Store(addr, value))
    elif op == 'LABEL':
        label = components[1]
        if label in labels:
            block = labels[block]
        else:
            block = BasicBlock([])
            labels[label] = block
        instructions.append(Jump(block))
        instructions = block.instructions
    elif op == 'ADDRG':
        label = components[1]
        if label not in labels:
            labels[label] = BasicBlock([])
        instructions.append(labels[label])
    elif op == 'JUMP':
        dest = instructions.pop()
        instructions.append(Jump(dest))
        block = BasicBlock([])
        instructions = block.instructions

    read()

def pprint(x):
    print(FormatCode(repr(x))[0])

print("Start:")
pprint(start)
