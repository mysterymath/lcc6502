from attr import attrs, attrib, Factory
from collections import defaultdict
from operator import itemgetter
import itertools
import textwrap


@attrs
class Func:
    name = attrib()
    inputs = attrib()
    blocks = attrib()

    def __str__(self):
        body = strcat(*self.inputs, *self.blocks)
        body = textwrap.indent(body, '  ')
        return f'{self.name}\n{body}end\n'


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
    size = attrib()
    args = attrib()

    def is_terminator(self):
        return self.op in ('br', 'ret', 'jsr', 'rts')

    def __str__(self):
        if self.op == 'phi':
            arg_tuples = []
            for i in range(0, len(self.args), 2):
                arg_tuples.append(tuple(self.args[i:i+2]))
            arg_tuples.sort(key=itemgetter(0))
            args = [a for t in arg_tuples for a in t]
        else:
            args = self.args

        results_str = f'{unsplit(self.results)} = ' if self.results else ''
        op_str = f'{self.op}{self.size}' if self.size is not None else self.op
        args_str = ' ' + unsplit(args) if args else ''
        return f'{results_str}{op_str}{args_str}\n'


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



def collect_predecessors(blocks):
    preds = defaultdict(set)
    for block in blocks:
        term = block.cmds[-1]
        if term.op == 'br':
            if len(term.args) == 1:
                preds[term.args[0]].add(block)
            else:
                preds[term.args[1]].add(block)
                preds[term.args[2]].add(block)
        elif term.op == 'jsr':
            preds[term.args[0]].add(block)
        elif term.op == 'rts':
            for a in term.args:
                preds[a].add(block)
    return preds


def remove_copies(blocks):
    # Collect and remove copies
    copies = {}
    for block in blocks:
        for cmd in block.cmds:
            if cmd.op == 'copy':
                (result,) = cmd.results
                (arg,) = cmd.args
                copies[result] = arg
        block.cmds = list(filter(lambda c: c.op != 'copy', block.cmds))

    is_closed = False
    while not is_closed:
        is_closed = True
        for copy, val in copies.items():
            if val in copies:
                copies[copy] = copies[val]
                is_closed = False

    # Propagate uses of copies
    for block in blocks:
        for cmd in block.cmds:
            def relabel(val):
                if val in copies:
                    return copies[val]
                return val
            cmd.args = list(map(relabel, cmd.args))


def new_name(name, defns):
    if name == '_':
        return name
    candidates = itertools.chain([name], (f'{name}{n}' for n in itertools.count(1)))
    chosen = next(c for c in candidates if c not in defns)
    defns.add(chosen)
    return chosen


def strcat(*args):
    return ''.join(map(str, args))


def unsplit(l):
    return ' '.join(map(str, l))
