import ir


def merge(start):
    uniquely_referenced_blocks = compute_uniquely_referenced_blocks(start)
    visited_blocks = set()
    block = start
    while block not in visited_blocks:
        visited_blocks.add(block)
        while block.terminator.destination in uniquely_referenced_blocks:
            destination = block.terminator.destination
            del block.instructions[-1]
            block.instructions.extend(destination.instructions)
        block = block.terminator.destination


def compute_uniquely_referenced_blocks(start):
    already_referenced = {
        start,
    }
    multiply_referenced = set()
    for block in ir.blocks_dfs(start):
        destination = block.terminator.destination

        if destination in already_referenced:
            multiply_referenced.add(destination)
        else:
            already_referenced.add(destination)

    return set(ir.blocks_dfs(start)) - multiply_referenced
