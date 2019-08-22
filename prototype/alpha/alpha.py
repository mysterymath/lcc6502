from attr import attrs, attrib, Factory
from collections import defaultdict, Counter
import fileinput
import re
import textwrap
import itertools


debug_line = None


class ParseError(Exception):
    pass


@attrs
class Func:
    name = attrib()
    inputs = attrib()
    blocks = attrib()

    def __str__(self):
        body = strcat(*self.inputs, *self.blocks)
        body = textwrap.indent(body, '  ')
        return f'{self.name}\n{body}end\n'


@attrs
class Input:
    name = attrib()
    size = attrib()

    def __str__(self):
        return f'input {self.name} {self.size}\n'


@attrs(cmp=False)
class Block:
    name = attrib()
    cmds = attrib(repr=False)

    def __str__(self):
        body = textwrap.indent(strcat(*self.cmds), '  ')
        return f'{self.name}\n{body}'


@attrs
class Cmd:
    results = attrib()
    op = attrib()
    args = attrib()

    def is_terminator(self):
        return self.op in ('br', 'ret')

    def __str__(self):
        results_str = f'{unsplit(self.results)} = ' if self.results else ''
        args_str = ' ' + unsplit(self.args) if self.args else ''
        return f'{results_str}{self.op}{args_str}\n'


@attrs
class Asm(Cmd):
    inputs = attrib()
    clobbers = attrib()
    instrs = attrib()

    def __str__(self):
        inputs = f'inputs {unsplit(self.inputs)}\n' if self.inputs else ''
        clobbers = f'clobbers {unsplit(self.clobbers)}\n' if self.clobbers else ''
        body = strcat(inputs, clobbers, *self.instrs)
        body = textwrap.indent(body, '  ')
        cmd_str = super().__str__()
        return f'{cmd_str}{body}end\n'


@attrs
class AsmInstr:
    op = attrib()
    args = attrib()

    def __str__(self):
        return f'{self.op} {unsplit(self.args)}\n'


def read_lines():
    global debug_line
    for line in fileinput.input():
        line = line.strip()
        if not line:
            continue
        debug_line = line
        yield line


def parse():
    rest = read_lines()
    first = next(rest)
    return parse_funcs(first, rest)


def parse_funcs(first, rest):
    funcs = []
    while True:
        funcs.append(parse_func(first, rest))
        try:
            first = next(rest)
        except StopIteration:
            return funcs


def parse_func(first, rest):
    (name,) = first.split()
    first = next(rest)

    inputs = []
    while first.split()[0] == 'input':
        inputs.append(parse_input(first, rest))
        first = next(rest)

    blocks = parse_section(first, rest, parse_block)
    return Func(name, inputs, blocks)


def parse_input(first, rest):
    (_, name, size) = first.split()
    return Input(name, size)


def parse_block(first, rest):
    (name,) = first.split()
    first = next(rest)
    cmds = parse_cmds(first, rest)
    return Block(name, cmds)


def parse_cmds(first, rest):
    cmds = []
    while True:
        cmd = parse_cmd(first, rest)
        cmds.append(cmd)
        if cmd.is_terminator():
            return cmds
        first = next(rest)


def parse_cmd(first, rest):
    (results, expr) = re.fullmatch(r'(?:(.*) = )?(.*)', first).groups()
    results = results.split() if results else []
    (op, *args) = expr.split()
    if op == 'asm':
        return parse_asm(first, rest, results, args)
    return Cmd(results, op, args)


def parse_asm(first, rest, results, args):
    first = next(rest)

    inputs = []
    clobbers = []
    if first.split()[0] == 'input':
        inputs.append(first.split()[1:])
        first = next(rest)
    if first.split()[0] == 'clobbers':
        clobbers.append(first.split()[1:])
        first = next(rest)

    instrs = parse_section(first, rest, parse_asm_instr)

    return Asm(results, 'asm', args, inputs, clobbers, instrs)


def parse_asm_instr(first, rest):
    (op, *args) = first.split()
    return AsmInstr(op, args)


def parse_section(first, rest, parse_item):
    items = []
    while True:
        items.append(parse_item(first, rest))
        first = next(rest)
        if first == 'end':
            return items


def to_ssa(func):
    # SSA values that have been already defined.
    defns = set()

    # A map from a pre-ssa variable to all its post-ssa definitions.
    new_values = defaultdict(set)

    # Given a pre-ssa definition label, assign a new label to it. This gives
    # each static definition a unique global label.
    def renumber(result):
        if result == '_':
            return result
        candidates = itertools.chain([result], (f'{result}{n}' for n in itertools.count(1)))
        chosen = next(c for c in candidates if c not in defns)
        defns.add(chosen)
        new_values[result].add(chosen)
        return chosen

    # Renumber all definitions.
    for block in func.blocks:
        for cmd in block.cmds:
            cmd.results = list(map(renumber, cmd.results))

    relabel_uses(func, new_values, renumber)

# Replace each use of an old value with the corresponding relabeled value.
# Inserts phi instructions as necessary.
def relabel_uses(func, new_values, renumber):
    preds = collect_predecessors(func)

    # Look up the reaching definition of a value at a given command.
    def lookup_renumbered_value(val, cmd_index, block):
        # Handle constants, block refs, anything not defined by a cmd.
        if val not in new_values:
            return val

        # If the value is defined in this block, return the
        # latest definition.
        for i in range(cmd_index-1, -1, -1):
            for r in block.cmds[i].results:
                if r in new_values[val]:
                    return r

        # Value not defined in block, so insert an phi without any
        # arguments.
        new_v = renumber(val)
        args = []
        phi = Cmd([new_v], 'phi', args)
        block.cmds.insert(0, phi)

        # Recursively look up the arguments of the phi. Since the phi
        # was already inserted, it will terminate any loops in the
        # dataflow graph by referencing itself.
        for pred in preds[block.name]:
            args.append(pred.name)
            args.append(lookup_value_from_end(val, pred))
        return new_v

    # Look up reaching definition of a value from the end of a block.
    def lookup_value_from_end(val, block):
        return lookup_renumbered_value(val, len(block.cmds), block)

    for block in func.blocks:
        while True:
            for cmd_index, cmd in enumerate(block.cmds):
                if cmd.op == 'phi':
                    continue
                def lookup_value(val):
                    return lookup_renumbered_value(val, cmd_index, block)
                old_size = len(block.cmds)
                cmd.args = list(map(lookup_value, cmd.args))
                if len(block.cmds) != old_size:
                    break
            else:
                break

    # Remove redundant phi instructions and relabel their uses iteratively
    # until none are left.
    while True:
        redundant_phis = collect_redundant_phis(func)
        if not redundant_phis:
            break
        remove_redundant_phis(func, redundant_phis)
        relabel_redundant_phi_uses(func, redundant_phis)

    remove_copies(func)


def collect_redundant_phis(func):
    redundant_phis = {}
    for block in func.blocks:
        for cmd in block.cmds:
            if cmd.op != 'phi':
                continue
            (result,) = cmd.results
            is_redundant = True
            real_arg = None
            for arg in cmd.args[1::2]:
                if arg == result:
                    continue
                elif real_arg is None:
                    real_arg = arg
                elif real_arg != arg:
                    is_redundant = False
                    break
            if is_redundant:
                redundant_phis[result] = real_arg
    return redundant_phis


def strcat(*args):
    return ''.join(map(str, args))


def unsplit(l):
    return ' '.join(map(str, l))


def collect_predecessors(func):
    preds = defaultdict(set)
    for block in func.blocks:
        term = block.cmds[-1]
        if term.op == 'br':
            if len(term.args) == 1:
                preds[term.args[0]].add(block)
            else:
                preds[term.args[1]].add(block)
                preds[term.args[2]].add(block)
    return preds


def remove_redundant_phis(func, redundant_phis):
    for block in func.blocks:
        def is_not_redundant_phi(cmd):
            if cmd.op != 'phi':
                return True
            (result,) = cmd.results
            return result not in redundant_phis
        block.cmds = list(filter(is_not_redundant_phi, block.cmds))


def relabel_redundant_phi_uses(func, redundant_phis):
    def relable_redundant_phi_arg(arg):
        if arg not in redundant_phis:
            return arg
        return redundant_phis[arg]
    for block in func.blocks:
        for cmd in block.cmds:
            cmd.args = list(map(relable_redundant_phi_arg, cmd.args))


def remove_copies(func):
    # Collect and remove copies
    copies = {}
    for block in func.blocks:
        for cmd in block.cmds:
            if cmd.op == 'copy':
                (result,) = cmd.results
                (arg,) = cmd.args
                copies[result] = arg
        block.cmds = list(filter(lambda c: c.op != 'copy', block.cmds))

    # Propagate uses of copies
    for block in func.blocks:
        for cmd in block.cmds:
            def relabel(val):
                if val in copies:
                    return copies[val]
                return val
            cmd.args = list(map(relabel, cmd.args))


def compute_live_sets(func):
    defns = {i.name for i in func.inputs}
    for block in func.blocks:
        block.live_in = set()
        block.live_out = set()
        for cmd in block.cmds:
            defns |= set(cmd.results)

    preds = collect_predecessors(func)

    is_done = False
    while not is_done:
        is_done = True
        for block in func.blocks:
            live = block.live_out.copy()
            for cmd in reversed(block.cmds):
                live -= set(cmd.results)
                if cmd.op != 'phi':
                    live |= set(cmd.args) & defns
            block.live_in = live.copy()

            for pred in preds[block.name]:
                old_size = len(pred.live_out)

                pred.live_out |= block.live_in
                for cmd in block.cmds:
                    if cmd.op != 'phi':
                        continue
                    for a_block, a in zip(cmd.args[::2], cmd.args[1::2]):
                        if a_block == pred.name:
                            pred.live_out |= {a} & defns

                if len(pred.live_out) != old_size:
                    is_done = False



try:
    funcs = parse()
except Exception as e:
    raise ParseError(f'{fileinput.filename()}:{fileinput.lineno()}: {debug_line}') from e

for func in funcs:
    to_ssa(func)
    print(func)

    compute_live_sets(func)
    for block in func.blocks:
        print(block.name)
        print('In:')
        print(block.live_in)
        print('Out:')
        print(block.live_out)
        print()
