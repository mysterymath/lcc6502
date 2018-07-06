import attr
import re
import sys
from attr import attrs, attrib
from collections import defaultdict
from numbers import Number
from yapf.yapflib.yapf_api import FormatCode

class ParseError(Exception):
    pass

def read():
    global line
    line = sys.stdin.readline().strip()

def expect(expected):
    global line
    if line != expected:
        raise ParseError("Expected: '{}'. Actual: '{}'".format(expected, line))
    read()

def expect_startswith(expected):
    global line
    if not line.startswith(expected):
        raise ParseError("Expected to start with: '{}'. Actual: '{}'".format(expected, line))
    read()

read()
expect("export main")
expect("code")
expect_startswith("proc main")

@attrs(cmp=False)
class Store(object):
    address = attrib()
    value = attrib()

@attrs(cmp=False)
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
while not line.startswith("endproc main"):
    if not line:
        raise ParseError("Expected: 'endproc main \d \d'. Found: EOF")
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
    else:
        raise ParseError("Unsupported operation: {}".format(operation))

    read()

def pprint(x):
    print(FormatCode(repr(x))[0], end='')

@attrs
class LoadAImmediate(object):
    value = attrib()

    def emit(self):
        print("lda #{}".format(self.value))

# Note: This includes absolute zero page stores.
@attrs
class StoreAAbsolute(object):
    address = attrib()

    def emit(self):
        print("sta {}".format(self.address))

@attrs
class JumpAbsolute(object):
    destination = attrib()

    def emit(self, block_ids):
        print("jmp _{}".format(block_ids[self.destination]))

# Select instructions for each basic block, from start to end.

# TODO: Track resources used and prevent clobbering.

@attrs(frozen=True)
class State(object):
    # A frozenset of register-contents pairs.
    registers = attrib()

    # Instructions used to reach the given state.
    instructions = attrib()
    done = attrib(default=False)

    @property
    def key(self):
        return self.registers, self.done

class InstructionSelectionError(Exception):
    pass

visited_blocks = set()
block = start
while True:
    if block in visited_blocks:
        break
    visited_blocks.add(block)

    instructions = []
    for instruction in block.instructions:
        # Perform a best-first search to select and schedule instructions for given DAG.

        # Search states already optimally reached.
        closed = set()

        # States yet to be exampined. A dictionary from cost to list of states.
        # There may be duplicates for each state; these are resolved when the state is popped.
        # This avoids maintaining an expensive priority queue, at the cost of using additional memory.
        frontier = defaultdict(list)

        # Add the empty state to start.
        frontier[0].append(State(frozenset(), tuple()))

        # Value of the lowest cost known to contain a state in the frontier.
        cur_cost = 0

        done = False
        while not done:
            # If the frontier is empty, then there was no way to cover the graph.
            if not frontier:
                raise InstructionSelectionError("No way found to implement instruction: {}".format(instruction))

            # Find the next lowest cost in the frontier
            while cur_cost not in frontier:
                cur_cost += 1

            # Pull the next best item out of the frontier.
            state = frontier[cur_cost].pop()
            if not frontier[cur_cost]:
                del frontier[cur_cost]

            # If we have already handled this state, a better path to it has already been found.
            if state.key in closed:
                continue
            # Otherwise, we now have found the best path to this state.
            closed.add(state.key)

            # If the instruction graph root is covered, we have found optimal instructions for the whole graph.
            if state.done:
                instructions += state.instructions
                done = True
                break

            # Consider adding LoadAImmediate
            if isinstance(instruction, Store):
                value = instruction.value
                if isinstance(value, Number):
                    next_cost = cur_cost + 2
                    next_registers = state.registers | {('A', value)}
                    next_instructions = state.instructions + (LoadAImmediate(value),)
                    frontier[next_cost].append(State(next_registers, next_instructions))

            # Consider adding StoreAAbsolute
            if isinstance(instruction, Store):
                address = instruction.address
                value = instruction.value
                if isinstance(address, Number) and ('A', value) in state.registers:
                    next_cost = cur_cost + (3 if instruction.address < 256 else 4)
                    next_instructions = state.instructions + (StoreAAbsolute(address),)
                    frontier[next_cost].append(State(state.registers, next_instructions, done=True))

            # Consider adding JumpAbsolute
            if isinstance(instruction, Jump):
                next_cost = cur_cost + 3
                next_instructions = state.instructions + (JumpAbsolute(instruction.destination),)
                frontier[next_cost].append(State(state.registers, next_instructions, done=True))


    terminator = block.terminator
    block.instructions = instructions

    # Jump is currently the only supported block terminator.
    assert isinstance(terminator, Jump)
    block = terminator.destination

# Emit prologue.
print(".word $FFFF")
print("start = $0700")
print(".word start")
print(".word end - 1")
print("* = start")

# Emit code for each basic block, from start to end.

block_ids = {}

block = start
while True:
    # Emit a label for each block.
    if block not in block_ids:
        block_ids[block] = len(block_ids)
    print("_{}:".format(block_ids[block]))

    # Emit instructions (except terminator).
    for instruction in block.instructions[:-1]:
        instruction.emit()

    # JumpAbsolute is currently the only supported block terminator.
    assert isinstance(block.terminator, JumpAbsolute)

    if block.terminator.destination in block_ids:
        # Jumps to already-emitted blocks must be emitted.
        block.terminator.emit(block_ids)
        # Since all jumps are currently unconditional, the first backward jump starts an infinite loop.
        # This means we are done.
        break
    else:
        # Jumps to not-yet-emitted blocks can be handled using fall-through.
        # This requires emitting the destination next.
        block = block.terminator.destination

# Emit epilogue.
print("end = *")
