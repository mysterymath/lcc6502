import ir


def compute(module):
    # Add the stack pointer.
    sp = ir.Global('sp', size=2)
    module.globals_.add(sp)

    for function in module.functions:
        # Compute the size to allocate for locals.
        locals_size = 0
        for block in ir.blocks_dfs(function.start):
            for instruction in ir.instructions_dfs(block):
                if (isinstance(instruction, ir.Load)
                        or isinstance(instruction, ir.Store)) and isinstance(
                            instruction.address, ir.Local):
                    locals_size = max(
                        locals_size,
                        instruction.address.index + instruction.size)

        # Decrease the stack pointer to allocate locals.
        if locals_size != 0:
            function.start.instructions.insert(
                0, ir.Store(2, sp, ir.Subtract(2, ir.Load(2, sp),
                                               locals_size)))

        # Replace local and parameter references with offsets from the stack pointer.
        for block in ir.blocks_dfs(function.start):
            for instruction in block.instructions:

                def replace(instruction):
                    if isinstance(instruction, ir.Local) or isinstance(
                            instruction, ir.Parameter):
                        offset = instruction.index
                        if isinstance(instruction, ir.Parameter):
                            offset += locals_size
                        if offset == 0:
                            return sp
                        else:
                            return ir.Add(2, sp, offset)
                    else:
                        return instruction

                ir.replace(instruction, replace)

        # Place stack cleanup before each return.
        if locals_size != 0:
            for block in ir.blocks_dfs(function.start):
                if isinstance(block.terminator, ir.Return):
                    block.instructions.insert(
                        len(block.instructions) - 1,
                        ir.Store(2, sp, ir.Add(2, ir.Load(2, sp),
                                               locals_size)))
