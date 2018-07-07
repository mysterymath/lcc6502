import attr
import re
import sys
from attr import attrs, attrib
from copy import deepcopy
from collections import defaultdict
from numbers import Number
from yapf.yapflib.yapf_api import FormatCode


def pprint(x):
    print(FormatCode(repr(x))[0], end='')


@attrs(cmp=False)
class Store(object):
    address = attrib()
    value = attrib()
    size = attrib()


@attrs(cmp=False)
class Jump(object):
    destination = attrib()


@attrs(frozen=True)
class Return(object):
    pass


@attrs(cmp=False)
class Call(object):
    destination = attrib()
    arguments = attrib()


@attrs(cmp=False)
class AsmCall(object):
    address = attrib()
    A = attrib()
    X = attrib()
    Y = attrib()


@attrs(frozen=True)
class Parameter(object):
    index = attrib()


@attrs(cmp=False)
class Argument(object):
    value = attrib()


@attrs(cmp=False)
class BasicBlock(object):
    instructions = attrib()

    @property
    def terminator(self):
        return self.instructions[-1]


@attrs(cmp=False)
class Function(object):
    name = attrib()
    start = attrib()


class ParseError(Exception):
    pass


def advance():
    global line
    line = sys.stdin.readline().strip()


labels = {}


def resolve_block(label):
    if label not in labels:
        labels[label] = BasicBlock([])
    return labels[label]


def resolve_function(label):
    if label not in labels:
        labels[label] = Function(label, BasicBlock([]))
    return labels[label]


def parse_function():
    name = line.split()[1]

    block = resolve_function(name).start
    instructions = block.instructions
    advance()

    try:
        while not line.startswith("endproc"):
            if not line:
                raise ParseError(
                    "Expected: 'endproc {}...'. Found: EOF".format(name))
            components = line.split()
            match = re.match("(\w+)(\D)(\d)?", components[0])
            operation = match[1]
            size = match[3] and int(match[3])

            if operation == 'CNST':
                instructions.append(int(components[1]))
            elif operation == 'ASGN':
                value = instructions.pop()
                address = instructions.pop()
                # Assignments to formal parameters are not yet handled.
                if not isinstance(address, Parameter):
                    if not size:
                        raise ParseError("ASGN requires a size; found none.")
                    instructions.append(Store(address, value, size))
            elif operation == 'LABEL':
                block = resolve_block(components[1])
                if instructions is not None:
                    instructions.append(Jump(block))
                instructions = block.instructions
            elif operation == 'ADDRF':
                instructions.append(Parameter(int(components[1])))
            elif operation == 'ADDRG':
                instructions.append(components[1])
            elif operation == 'JUMP':
                label = instructions.pop()
                instructions.append(Jump(resolve_block(label)))
                block = None
                instructions = None
            elif operation == 'INDIR':
                pass
            elif operation == 'ARG':
                instructions.append(Argument(instructions.pop()))
            elif operation.startswith('CV'):
                pass
            elif operation == 'CALL':
                label = instructions.pop()

                arguments = []
                while instructions and isinstance(instructions[-1], Argument):
                    arguments.append(instructions.pop().value)
                arguments.reverse()

                if label == '__asm_call':

                    def ArgFn(arg):
                        if not isinstance(arg, Number):
                            return arg
                        if arg >= 0:
                            return arg

                    instructions.append(
                        AsmCall(arguments[0], *map(ArgFn, arguments[1:])))
                else:
                    if label not in labels:
                        labels[label] = Function(label, BasicBlock([]))
                    instructions.append(Call(labels[label], arguments))
            else:
                raise ParseError("Unsupported operation: {}".format(operation))

            advance()
    except ParseError as e:
        raise ParseError("Could not parse function {}".format(name)) from e
    advance()

    # If the block does not already have a terminator, add a Return.
    if not instructions or not isinstance(block.terminator, Jump):
        instructions.append(Return())


advance()

while line:
    if line.startswith("proc"):
        parse_function()
    else:
        advance()

functions = {v for v in labels.values() if isinstance(v, Function)}


def blocks_dfs(start):
    blocks = []
    block = start
    while block not in blocks:
        blocks.append(block)
        if isinstance(block.terminator, Return):
            break
        block = block.terminator.destination
    return blocks


def is_leaf_function(value):
    if not isinstance(value, Function):
        return False

    for block in blocks_dfs(value.start):
        for instruction in block.instructions:
            if isinstance(instruction, Call):
                return False
    return True


def inline_call(call, next_block):
    start = deepcopy(call.destination.start)

    for block in blocks_dfs(start):
        for instruction in block.instructions:
            # TODO: This should modify everywhere a parameter can appear. Need a real visitor.
            if isinstance(instruction, AsmCall):
                if isinstance(instruction.A, Parameter):
                    instruction.A = call.arguments[instruction.A.index]
        if isinstance(block.terminator, Return):
            block.instructions[-1] = Jump(next_block)
    return start


def inline_leaf_functions(leaf_functions):
    inlined_any = False
    for function in functions:
        for block in blocks_dfs(function.start):
            instructions = []
            for i, instruction in enumerate(block.instructions):
                if isinstance(
                        instruction,
                        Call) and instruction.destination in leaf_functions:
                    next_block = BasicBlock(block.instructions[i + 1:])
                    inline_block = inline_call(instruction, next_block)
                    instructions.append(Jump(inline_block))
                    inlined_any = True
                    break
                else:
                    instructions.append(instruction)
            block.instructions = instructions
    return inlined_any


while True:
    leaf_functions = set(filter(is_leaf_function, functions))
    if not inline_leaf_functions(leaf_functions):
        break

start = labels['main'].start

# Lower each basic block sizes to single bytes, from start to end.


class LoweringError(Exception):
    pass


for block in blocks_dfs(start):
    instructions = []
    for instruction in block.instructions:
        if isinstance(instruction, Store) and instruction.size > 1:
            value = instruction.value
            address = instruction.address
            if instruction.size == 2 and isinstance(
                    address, Number) and isinstance(value, Number):
                instructions.append(Store(address, value % 256, 1))
                instructions.append(Store(address + 1, value // 256, 1))
            else:
                raise LoweringError("Could not lower: {}".format(instruction))
        else:
            instructions.append(instruction)
    block.instructions = instructions

# Select instructions for each basic block, from start to end.


@attrs
class LoadImmediate(object):
    register = attrib()
    value = attrib()

    def emit(self):
        print("ld{} #{}".format(self.register.lower(), self.value))


# Note: This includes absolute zero page stores.
@attrs
class StoreAbsolute(object):
    register = attrib()
    address = attrib()

    def emit(self):
        print("st{} {}".format(self.register.lower(), self.address))


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
num_closed = 0

for block in blocks_dfs(start):
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

    while True:
        # If the frontier is empty, then there was no way to cover the graph.
        if not frontier:
            raise InstructionSelectionError(
                "No way found to implement block: {}".format(block))

        # Find the next lowest cost in the frontier
        while cur_cost not in frontier:
            cur_cost += 1

        # Pull the next best item out of the frontier.
        state = frontier[cur_cost].pop()
        if not frontier[cur_cost]:
            del frontier[cur_cost]

        # If we have already handled this state, a better path to it has already been found.
        if state.key in closed:
            num_closed += 1
            continue
        # Otherwise, we now have found the best path to this state.
        closed.add(state.key)

        num_iter += 1

        # If the instruction graph root is covered, we have found optimal instructions for the whole graph.
        if state.next_instruction_index == len(block.instructions):
            block.instructions = state.instructions
            break

        def update_state(cost, state):
            if state.key not in closed:
                frontier[cost].append(state)

        instruction = block.instructions[state.next_instruction_index]

        # Consider adding LoadImmediate
        def ConsiderLoadImmediate(register, value):
            if not isinstance(value, Number):
                return
            next_cost = cur_cost + 2
            next_registers = state.registers | {(register, value)}
            next_instructions = state.instructions + (LoadImmediate(
                register, value), )
            update_state(
                next_cost,
                State(next_registers, state.next_instruction_index,
                      next_instructions))

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

        # Consider adding StoreAbsolute
        def ConsiderStoreAbsolute(register, address, value):
            if isinstance(address, Number) and (register,
                                                value) in state.registers:
                next_cost = cur_cost + (3 if address < 256 else 4)
                next_instructions = state.instructions + (StoreAbsolute(
                    register, address), )
                update_state(
                    next_cost,
                    State(state.registers, state.next_instruction_index + 1,
                          next_instructions))

        if isinstance(instruction, Store):
            ConsiderStoreAbsolute('A', instruction.address, instruction.value)
            ConsiderStoreAbsolute('X', instruction.address, instruction.value)
            ConsiderStoreAbsolute('Y', instruction.address, instruction.value)

        # Consider adding JumpAbsolute
        if isinstance(instruction, Jump):
            next_cost = cur_cost + 3
            next_instructions = state.instructions + (JumpAbsolute(
                instruction.destination), )
            update_state(
                next_cost,
                State(state.registers, state.next_instruction_index + 1,
                      next_instructions))

        # Consider adding JumpSubroutine
        if isinstance(instruction, AsmCall):

            def try_apply():
                if instruction.A is not None and (
                        'A', instruction.A) not in state.registers:
                    return
                if instruction.X is not None and (
                        'X', instruction.X) not in state.registers:
                    return
                if instruction.Y is not None and (
                        'Y', instruction.Y) not in state.registers:
                    return
                next_cost = cur_cost + 6
                next_instructions = state.instructions + (JumpSubroutine(
                    instruction.address), )
                # To be safe, assume that calls clear all computed values.
                # TODO: Clobbered register annotations.
                update_state(
                    next_cost,
                    State(frozenset(), state.next_instruction_index + 1,
                          next_instructions))

            try_apply()

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
print("Num iter: {}".format(num_iter), file=sys.stderr)
print("Num closed: {}".format(num_closed), file=sys.stderr)
