import sys
from attr import attrs, attrib
from collections import defaultdict
from numbers import Number
from yapf.yapflib.yapf_api import FormatCode

import ir
import parser
import inliner
import lowerer
import asm


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

for block in ir.blocks_dfs(start):
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
            next_instructions = state.instructions + (asm.LoadImmediate(
                register, value), )
            update_state(
                next_cost,
                State(next_registers, state.next_instruction_index,
                      next_instructions))

        if isinstance(instruction, ir.Store):
            ConsiderLoadImmediate('A', instruction.value)
            ConsiderLoadImmediate('X', instruction.value)
            ConsiderLoadImmediate('Y', instruction.value)
        elif isinstance(instruction, ir.AsmCall):
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
                next_instructions = state.instructions + (asm.StoreAbsolute(
                    register, address), )
                update_state(
                    next_cost,
                    State(state.registers, state.next_instruction_index + 1,
                          next_instructions))

        if isinstance(instruction, ir.Store):
            ConsiderStoreAbsolute('A', instruction.address, instruction.value)
            ConsiderStoreAbsolute('X', instruction.address, instruction.value)
            ConsiderStoreAbsolute('Y', instruction.address, instruction.value)

        # Consider adding JumpAbsolute
        if isinstance(instruction, ir.Jump):
            next_cost = cur_cost + 3
            next_instructions = state.instructions + (asm.JumpAbsolute(
                instruction.destination), )
            update_state(
                next_cost,
                State(state.registers, state.next_instruction_index + 1,
                      next_instructions))

        # Consider adding JumpSubroutine
        if isinstance(instruction, ir.AsmCall):

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
                next_instructions = state.instructions + (asm.JumpSubroutine(
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


class EmitError(Exception):
    pass


def emit(instruction):
    if isinstance(instruction, asm.LoadImmediate):
        print("ld{} #{}".format(instruction.register.lower(),
                                instruction.value))
    elif isinstance(instruction, asm.StoreAbsolute):
        print("st{} {}".format(instruction.register.lower(),
                               instruction.address))
    elif isinstance(instruction, asm.JumpSubroutine):
        print("jsr {}".format(instruction.address))
    else:
        raise EmitError("Could not emit instruction {}".format(instruction))


block_ids = {}

block = start
while True:
    # Emit a label for each block.
    if block not in block_ids:
        block_ids[block] = len(block_ids)
    print("_{}:".format(block_ids[block]))

    # Emit instructions (except terminator).
    for instruction in block.instructions[:-1]:
        emit(instruction)

    # JumpAbsolute is currently the only supported block terminator.
    assert isinstance(block.terminator, asm.JumpAbsolute)

    if block.terminator.destination in block_ids:
        # Jumps to already-emitted blocks must be emitted.
        print("jmp _{}".format(block_ids[block.terminator.destination]))
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
