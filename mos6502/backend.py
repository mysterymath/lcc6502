import pprint
import re
import sys
from attr import attrs, attrib

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
class Instruction(object):
    op = attrib()
    type_ = attrib()
    size = attrib()
    args = attrib(default=None)


arity = {
    'ADDRG': 0,
    'CNST': 0,
    'ASGN': 2,
    'LABEL': 0,
    'JUMP': 1,
}


stack = []
while line != "endproc main 0 0":
    if not line:
        raise "Expected: 'endproc main 0 0'. Found: EOF"
    components = line.split()
    match = re.match("(\w+)(\D)(\d)?", components[0])
    instruction = Instruction(match[1], match[2], match[3] and int(match[3]))

    args = []
    for _ in range(arity[instruction.op]):
        args.append(stack.pop())
    args.reverse()
    instruction.args = args

    stack.append(instruction)
    read()

pprint.pprint(stack)
