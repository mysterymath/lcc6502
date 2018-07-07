from copy import deepcopy

import ir


def is_leaf_function(value):
    if not isinstance(value, ir.Function):
        return False

    for block in ir.blocks_dfs(value.start):
        for instruction in block.instructions:
            if isinstance(instruction, ir.Call):
                return False
    return True


def inline_call(call, next_block):
    start = deepcopy(call.destination.start)

    def replace(x):
        if isinstance(x, ir.Parameter):
            return call.arguments[x.index]
        if isinstance(x, ir.Return):
            return ir.Jump(next_block)
        return x

    for block in ir.blocks_dfs(start):
        for i in range(len(block.instructions)):
            block.instructions[i] = ir.replace(block.instructions[i], replace)
    return start


def inline_leaf_functions(leaf_functions, functions):
    inlined_any = False
    for function in functions:
        for block in ir.blocks_dfs(function.start):
            instructions = []
            for i, instruction in enumerate(block.instructions):
                if isinstance(
                        instruction,
                        ir.Call) and instruction.destination in leaf_functions:
                    next_block = ir.BasicBlock(block.instructions[i + 1:])
                    inline_block = inline_call(instruction, next_block)
                    instructions.append(ir.Jump(inline_block))
                    inlined_any = True
                    break
                else:
                    instructions.append(instruction)
            block.instructions = instructions
    return inlined_any


def inline(functions):
    while True:
        leaf_functions = set(filter(is_leaf_function, functions))
        if not inline_leaf_functions(leaf_functions, functions):
            return
