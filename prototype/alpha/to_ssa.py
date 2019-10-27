from collections import defaultdict
import itertools

from common import Cmd
from common import collect_predecessors, new_name, remove_copies

def to_ssa(blocks):
    # SSA values that have been already defined.
    defns = set()

    # A map from a pre-ssa variable to all its post-ssa definitions.
    new_values = defaultdict(set)

    # Given a pre-ssa definition label, assign a new label to it. This gives
    # each static definition a unique global label.
    def renumber(result):
        if result == '_':
            return result
        chosen = new_name(result, defns)
        new_values[result].add(chosen)
        return chosen

    # Renumber all definitions.
    for block in blocks:
        for cmd in block.cmds:
            cmd.results = list(map(renumber, cmd.results))

    relabel_uses(blocks, new_values, renumber)

# Replace each use of an old value with the corresponding relabeled value.
# Inserts phi instructions as necessary.
def relabel_uses(blocks, new_values, renumber):
    preds = collect_predecessors(blocks)

    rts_targets = set()
    for block in blocks:
        for cmd in block.cmds:
            if cmd.op != 'rts':
                continue
            rts_targets |= set(cmd.args)

    # Look up the reaching definition of a value at a given command.
    def lookup_renumbered_value(val, cmd_index, block, rts_stack):
        # Handle constants, block refs, anything not defined by a cmd.
        if val not in new_values:
            return val

        # If the value is defined in this block, return the
        # latest definition.
        for i in range(cmd_index-1, -1, -1):
            for r in block.cmds[i].results:
                if r in new_values[val]:
                    return r

        # Insert an phi without any arguments.
        new_v = renumber(val)
        args = []
        phi = Cmd([new_v], 'phi_tmp', None, args)
        block.cmds.insert(0, phi)

        # Recursively look up the arguments of the phi. Since the phi
        # was already inserted, it will terminate any loops in the
        # dataflow graph by referencing itself.
        for pred in preds[block.name]:
            if pred.cmds[-1].op == 'jsr' and rts_stack:
                if pred.cmds[-1].args[1] != rts_stack[-1]:
                    continue
                else:
                    args.append(pred.name)
                    args.append(lookup_value_from_end(val, pred, rts_stack[:-1]))
            else:
                args.append(pred.name)
                args.append(lookup_value_from_end(val, pred, rts_stack))
        return new_v

    # Look up reaching definition of a value from the end of a block.
    def lookup_value_from_end(val, block, rts_stack):
        if block.name in rts_targets:
            rts_stack += (block.name,)
        return lookup_renumbered_value(val, len(block.cmds), block, rts_stack)

    for block in blocks:
        while True:
            rts_stack = ()
            if block.name in rts_targets:
                rts_stack += (block.name,)
            for cmd_index, cmd in enumerate(block.cmds):
                # Only newly added phis should be skipped.
                if cmd.op == 'phi_tmp':
                    continue
                def lookup_value(val):
                    return lookup_renumbered_value(val, cmd_index, block, rts_stack)
                old_size = len(block.cmds)
                if cmd.op == 'phi':
                    for i in range(0, len(cmd.args), 2):
                        blk = cmd.args[i]
                        (blk,) = (b for b in blocks if b.name == cmd.args[i])
                        cmd.args[i+1] = lookup_value_from_end(cmd.args[i+1], blk, rts_stack)
                else:
                    cmd.args = list(map(lookup_value, cmd.args))
                if len(block.cmds) != old_size:
                    break
            else:
                break

    # Change all temporary phis back to regular phis.
    for block in blocks:
        for cmd in block.cmds:
            if cmd.op == 'phi_tmp':
                cmd.op = 'phi'

    # Remove redundant phi instructions and relabel their uses iteratively
    # until none are left.
    while True:
        redundant_phis = collect_redundant_phis(blocks)
        if not redundant_phis:
            break
        remove_redundant_phis(blocks, redundant_phis)
        relabel_redundant_phi_uses(blocks, redundant_phis)

    remove_copies(blocks)


def collect_redundant_phis(blocks):
    redundant_phis = {}
    for block in blocks:
        for cmd in block.cmds:
            if cmd.op != 'phi':
                continue
            (result,) = cmd.results
            is_redundant = True
            real_arg = None
            for arg in cmd.args[1::2]:
                if arg == result or arg == 'undef':
                    continue
                elif real_arg is None:
                    real_arg = arg
                elif real_arg != arg:
                    is_redundant = False
                    break
            if is_redundant:
                if real_arg is None:
                    real_arg = 'undef'
                redundant_phis[result] = real_arg

    is_closed = False
    while not is_closed:
        is_closed = True
        for phi, val in redundant_phis.items():
            if val in redundant_phis:
                redundant_phis[phi] = redundant_phis[val]
                is_closed = False

    return redundant_phis


def remove_redundant_phis(blocks, redundant_phis):
    for block in blocks:
        def is_not_redundant_phi(cmd):
            if cmd.op != 'phi':
                return True
            (result,) = cmd.results
            return result not in redundant_phis
        block.cmds = list(filter(is_not_redundant_phi, block.cmds))


def relabel_redundant_phi_uses(blocks, redundant_phis):
    def relable_redundant_phi_arg(arg):
        if arg not in redundant_phis:
            return arg
        return redundant_phis[arg]
    for block in blocks:
        for cmd in block.cmds:
            cmd.args = list(map(relable_redundant_phi_arg, cmd.args))
