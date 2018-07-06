import attr
import re
import sys
from attr import attrs, attrib
from collections import defaultdict
from numbers import Number
from yapf.yapflib.yapf_api import FormatCode

def pprint(x):
    print(FormatCode(repr(x))[0], end='')

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
    size = attrib()

@attrs(cmp=False)
class Jump(object):
    destination = attrib()

@attrs
class AsmCall(object):
    address = attrib()
    A = attrib()
    X = attrib()
    Y = attrib()

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
    size = match[3] and int(match[3])

    if operation == 'CNST':
        instructions.append(int(components[1]))
    elif operation == 'ASGN':
        value = instructions.pop()
        address = instructions.pop()
        if not size:
            raise ParseError("ASGN requires a size; found none.")
        instructions.append(Store(address, value, size))
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
        if label != '__asm_call':
            if label not in labels:
                labels[label] = BasicBlock([])
            instructions.append(labels[label])
    elif operation == 'JUMP':
        destination = instructions.pop()
        instructions.append(Jump(destination))
        block = BasicBlock([])
        instructions = block.instructions
    elif operation == 'ARG':
        pass
    elif operation == 'CALL':
        args = instructions[-4:]
        del instructions[-4:]
        instructions.append(AsmCall(args[0], *map(lambda arg: arg if arg >= 0 else None, args[1:])))
    else:
        raise ParseError("Unsupported operation: {}".format(operation))

    read()

# Lower each basic block sizes to single bytes, from start to end.

class LoweringError(Exception):
    pass

visited_blocks = set()
block = start
while True:
    if block in visited_blocks:
        break
    visited_blocks.add(block)

    instructions = []
    for instruction in block.instructions:
        if isinstance(instruction, Store) and instruction.size > 1:
            value = instruction.value
            address = instruction.address
            if instruction.size == 2 and isinstance(address, Number) and isinstance(value, Number):
                instructions.append(Store(address, value % 256, 1))
                instructions.append(Store(address + 1, value // 256, 1))
            else:
                raise LoweringError("Could not lower: {}".format(instruction))
        else:
            instructions.append(instruction)

    terminator = block.terminator
    block.instructions = instructions

    # Jump is currently the only supported block terminator.
    assert isinstance(terminator, Jump)
    block = terminator.destination

# Select instructions for each basic block, from start to end.

@attrs
class LoadImmediate(object):
    reg = attrib()
    value = attrib()

    def emit(self):
        print("ld{} #{}".format(self.reg.lower(), self.value))

# Note: This includes absolute zero page stores.
@attrs
class StoreAAbsolute(object):
    address = attrib()

    def emit(self):
        print("sta {}".format(self.address))

@attrs
class JumpSubroutine(object):
    address = attrib()

    def emit(self):
        print("jsr {}".format(self.address))

@attrs
class JumpAbsolute(object):
    destination = attrib()

    def emit(self, block_ids):
        print("jmp _{}".format(block_ids[self.destination]))


@attrs(frozen=True)
class State(object):
    # A frozenset of register-contents pairs.
    registers = attrib()

    # Index of the first instruction yet to be generated.
    next_instruction_index = attrib()

    # Instructions used to reach the given state.
    instructions = attrib()

    @property
    def key(self):
        return self.registers, self.next_instruction_index

class InstructionSelectionError(Exception):
    pass

num_iter = 0

visited_blocks = set()
block = start
while True:
    if block in visited_blocks:
        break
    visited_blocks.add(block)

    # Perform a best-first search to select and schedule instructions for given DAG.

    # Search states already optimally reached.
    closed = set()

    # States yet to be exampined. A dictionary from cost to list of states.
    # There may be duplicates for each state; these are resolved when the state is popped.
    # This avoids maintaining an expensive priority queue, at the cost of using additional memory.
    frontier = defaultdict(list)

    # Add the empty state to start.
    frontier[0].append(State(frozenset(), 0, tuple()))

    # Value of the lowest cost known to contain a state in the frontier.
    cur_cost = 0

    done = False
    while not done:
        # If the frontier is empty, then there was no way to cover the graph.
        if not frontier:
            raise InstructionSelectionError("No way found to implement block: {}".format(block))

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

        num_iter += 1

        # If the instruction graph root is covered, we have found optimal instructions for the whole graph.
        if state.next_instruction_index == len(block.instructions):
            instructions = state.instructions
            done = True
            break

        for instruction in block.instructions[state.next_instruction_index:]:
            # Consider adding LoadImmediate
            def ConsiderLoadImmediate(reg, value):
                if not isinstance(value, Number):
                    return
                next_cost = cur_cost + 2
                next_registers = state.registers | {(reg, value)}
                next_instructions = state.instructions + (LoadImmediate(reg, value),)
                frontier[next_cost].append(State(next_registers, state.next_instruction_index, next_instructions))
            if isinstance(instruction, Store):
                ConsiderLoadImmediate('A', instruction.value)
                ConsiderLoadImmediate('X', instruction.value)
                ConsiderLoadImmediate('Y', instruction.value)
            elif isinstance(instruction, AsmCall):
                if instruction.A is not None:
                    ConsiderLoadImmediate('A', instruction.A)
                if instruction.X is not None:
                    ConsiderLoadImmediate('X', instruction.X)
                if instruction.Y is not None:
                    ConsiderLoadImmediate('Y', instruction.Y)

            # Root instructions are executed for their side effects and cannot be scheduled before the previous. 
            if instruction is block.instructions[state.next_instruction_index]:
                # Consider adding StoreAAbsolute
                if isinstance(instruction, Store):
                    address = instruction.address
                    value = instruction.value
                    if isinstance(address, Number) and instruction.size == 1 and ('A', value) in state.registers:
                        next_cost = cur_cost + (3 if instruction.address < 256 else 4)
                        next_instructions = state.instructions + (StoreAAbsolute(address),)
                        frontier[next_cost].append(State(state.registers, state.next_instruction_index + 1, next_instructions))

                # Consider adding JumpAbsolute
                if isinstance(instruction, Jump):
                    next_cost = cur_cost + 3
                    next_instructions = state.instructions + (JumpAbsolute(instruction.destination),)
                    frontier[next_cost].append(State(state.registers, state.next_instruction_index + 1, next_instructions))

                # Consider adding JumpSubroutine
                if isinstance(instruction, AsmCall):
                    def try_apply():
                        if instruction.A is not None and ('A', instruction.A) not in state.registers:
                            return
                        if instruction.X is not None and ('X', instruction.X) not in state.registers:
                            return
                        if instruction.Y is not None and ('Y', instruction.Y) not in state.registers:
                            return
                        next_cost = cur_cost + 6
                        next_instructions = state.instructions + (JumpSubroutine(instruction.address),)
                        # To be safe, assume that calls clear all computed values.
                        # TODO: Clobbered register annotations.
                        frontier[next_cost].append(State(frozenset(), state.next_instruction_index + 1, next_instructions))
                    try_apply()


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

print("\n\nStats:", file=sys.stderr)
print("Num_iter: {}".format(num_iter), file=sys.stderr)
