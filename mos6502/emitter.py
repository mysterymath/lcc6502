import asm


class EmitError(Exception):
    pass


def emit(start):
    # Emit prologue.
    print(".word $FFFF")
    print("start = $0700")
    print(".word start")
    print(".word end - 1")
    print("* = start")

    block_ids = {}

    block = start
    while True:
        # Emit a label for each block.
        if block not in block_ids:
            block_ids[block] = len(block_ids)
        print("_{}:".format(block_ids[block]))

        # Emit instructions (except terminator).
        for instruction in block.instructions[:-1]:
            emit_instruction(instruction)

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


def emit_instruction(instruction):
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
