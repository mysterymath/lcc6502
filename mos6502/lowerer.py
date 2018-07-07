from numbers import Number

import ir


class LoweringError(Exception):
    pass


def lower(start):
    for block in ir.blocks_dfs(start):
        instructions = []
        for instruction in block.instructions:
            if isinstance(instruction, ir.Store) and instruction.size > 1:
                value = instruction.value
                address = instruction.address
                if instruction.size == 2 and isinstance(
                        address, Number) and isinstance(value, Number):
                    instructions.append(ir.Store(address, value % 256, 1))
                    instructions.append(ir.Store(address + 1, value // 256, 1))
                else:
                    raise LoweringError(
                        "Could not lower: {}".format(instruction))
            else:
                instructions.append(instruction)
        block.instructions = instructions
