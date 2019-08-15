from attr import attrs, attrib, Factory
import fileinput
import re
import textwrap


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
        name = f'{self.name}\n'
        inputs = textwrap.indent(''.join(map(str, self.inputs)), '  ')
        outputs = textwrap.indent(''.join(map(str, self.outputs)), '  ')
        blocks = textwrap.indent(''.join(map(str, self.blocks)), '  ')
        end = 'end\n'
        return ''.join([name, inputs, outputs, blocks, end])


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


@attrs
class Block:
    name = attrib()
    cmds = attrib()

    def __str__(self):
        cmd_str = textwrap.indent(''.join(map(str, self.cmds)), '  ')
        return f'{self.name}\n{cmd_str}'


@attrs
class Cmd:
    results = attrib()
    op = attrib()
    args = attrib()

    def is_terminator(self):
        return self.op in ('br', 'ret')

    def __str__(self):
        results_str = f'{" ".join(self.results)} = ' if self.results else ''
        return f'{results_str}{self.op} {" ".join(self.args)}\n'


@attrs
class Asm:
    inputs = attrib()
    clobbers = attrib()
    instrs = attrib()

    def __str__(self):
        begin_str = 'asm\n'
        inputs_str = textwrap.indent(''.join(map(str, self.inputs)), '  ')
        clobbers_str = textwrap.indent(f'clobbers {" ".join(map(str, self.clobbers))}\n', '  ')
        instrs_str = textwrap.indent(''.join(map(str, self.instrs)), '  ')
        end_str = 'end\n'

        return ''.join([begin_str, inputs_str, clobbers_str, instrs_str, end_str])


@attrs
class AsmInstr:
    op = attrib()
    args = attrib()

    def __str__(self):
        return f'{self.op} {" ".join(map(str, self.args))}\n'


@attrs
class AsmInput:
    register = attrib()
    value = attrib()

    def __str__(self):
        return f'input {self.register} {self.value}\n'


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

    blocks = parse_blocks(first, rest)
    return Func(name, inputs, outputs, blocks)


def parse_input(first, rest):
    (_, name, size) = first.split()
    return Input(name, size)


def parse_output(first, rest):
    (_, name, size) = first.split()
    return Output(name, size)


def parse_blocks(first, rest):
    blocks = []
    while True:
        blocks.append(parse_block(first, rest))
        first = next(rest)
        if first == 'end':
            return blocks


def parse_block(first, rest):
    (name,) = first.split()
    first = next(rest)
    cmds = parse_cmds(first, rest)
    return Block(name, cmds)


def parse_cmds(first, rest):
    cmds = []
    while True:
        if first == 'asm':
            cmd = parse_asm(first, rest)
            cmds.append(cmd)
        else:
            cmd = parse_cmd(first, rest)
            cmds.append(cmd)
            if cmd.is_terminator():
                return cmds
        first = next(rest)


def parse_cmd(first, rest):
    (results, expr) = re.fullmatch(r'(?:(.*) = )?(.*)', first).groups()
    results = results.split() if results else []
    (op, *args) = expr.split()
    return Cmd(results, op, args)


def parse_asm(first, rest):
    first = next(rest)

    inputs = []
    clobbers = []
    while first.split()[0] == 'input':
        inputs.append(parse_asm_input(first, rest))
        first = next(rest)
    if first.split()[0] == 'clobber':
        clobbers = parse_clobber(first, rest)
        first = next(rest)

    instrs = parse_asm_instrs(first, rest)

    return Asm(inputs, clobbers, instrs)


def parse_asm_input(first, rest):
    (_, register, value) = first.split()
    return AsmInput(register, value)


def parse_clobber(first, rest):
    return list(first.split()[1:])


def parse_asm_instrs(first, rest):
    instrs = []
    while True:
        instrs.append(parse_asm_instr(first, rest))
        first = next(rest)
        if first == 'end':
            return instrs


def parse_asm_instr(first, rest):
    (op, *args) = first.split()
    return AsmInstr(op, args)


try:
    funcs = parse()
except Exception as e:
    raise ParseError(f'{fileinput.filename()}:{fileinput.lineno()}: {debug_line}') from e
for func in funcs:
    print(func)
