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
    outputs = attrib()
    blocks = attrib()

    def __str__(self):
        body = strcat(*self.inputs, *self.outputs, *self.blocks)
        body = textwrap.indent(body, '  ')
        return f'{self.name}\n{body}end\n'


@attrs
class Input:
    name = attrib()
    size = attrib()

    def __str__(self):
        return f'input {self.name} {self.size}\n'


@attrs
class Output:
    name = attrib()
    size = attrib()

    def __str__(self):
        return f'output {self.name} {self.size}\n'


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
    outputs = []
    while first.split()[0] == 'input':
        inputs.append(parse_input(first, rest))
        first = next(rest)
    while first.split()[0] == 'output':
        outputs.append(parse_output(first, rest))
        first = next(rest)

    blocks = parse_section(first, rest, parse_block)
    return Func(name, inputs, outputs, blocks)


def parse_input(first, rest):
    (_, name, size) = first.split()
    return Input(name, size)


def parse_output(first, rest):
    (_, name, size) = first.split()
    return Output(name, size)


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
    defns = set()
    new_values = defaultdict(set)

    def renumber(result):
        if result == '_':
            return result
        candidates = (f'{result}{n}' for n in itertools.count(1))
        chosen = next(c for c in candidates if c not in defns)
        defns.add(chosen)
        new_values[result].add(chosen)
        return chosen


    for block in func.blocks:
        for cmd in block.cmds:
            cmd.results = list(map(renumber, cmd.results))

    # Copy to the real outputs of each function, which are no longer assigned to.
    # The arguments to these copies will be rewritten with the actual reaching
    # definitions.
    for block in func.blocks:
        term = block.cmds[-1]
        if term.op == 'ret':
            for o in func.outputs:
                block.cmds.insert(len(block.cmds)-1, Cmd([o.name], 'copy', [o.name]))

    preds = collect_predecessors(func)

    for block in func.blocks:
        for cmd_index, cmd in enumerate(block.cmds):
            def lookup_renumbered_value(val, cmd_index=cmd_index, block=block):
                if val not in new_values:
                    return val

                for i in range(cmd_index-1, -1, -1):
                    for r in block.cmds[i].results:
                        if r in new_values[val]:
                            return r

                # Value not defined in block, so insert a phi.
                # May be removed later.
                new_v = renumber(val)
                args = []
                phi = Cmd([new_v], 'phi', args)
                # Insert phi before args computed to terminate recursive lookups
                block.cmds.insert(0, phi)
                for pred in preds[block.name]:
                    args.append(pred.name)
                    args.append(lookup_renumbered_value(val, len(pred.cmds), pred))
                return new_v

            if cmd.op == 'br':
                if len(cmd.args) == 3:
                    cmd.args[0] = lookup_renumbered_value(cmd.args[0])
            elif cmd.op == 'call':
                cmd.args[1:] = list(map(lookup_renumbered_value, cmd.args[1:]))
            else:
                cmd.args = list(map(lookup_renumbered_value, cmd.args))

    while True:
        # Collect redundant phis.
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

        if not len(redundant_phis):
            break

        # Remove redundant phis.
        for block in func.blocks:
            def is_not_redundant_phi(cmd):
                if cmd.op != 'phi':
                    return True
                (result,) = cmd.results
                return result not in redundant_phis
            block.cmds = list(filter(is_not_redundant_phi, block.cmds))

        # Relable redundant phi usages.
        def relable_redundant_phi_arg(arg):
            if arg not in redundant_phis:
                return arg
            return redundant_phis[arg]
        for block in func.blocks:
            for cmd in block.cmds:
                cmd.args = list(map(relable_redundant_phi_arg, cmd.args))


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

try:
    funcs = parse()
except Exception as e:
    raise ParseError(f'{fileinput.filename()}:{fileinput.lineno()}: {debug_line}') from e

for func in funcs:
    to_ssa(func)
    print(func)

