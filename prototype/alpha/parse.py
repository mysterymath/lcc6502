import fileinput
import re

from common import Func, Block, Cmd, Asm, AsmInstr


class ParseError(Exception):
    pass


def parse():
    return Parser().parse()


class Parser:
    def __init__(self):
        self.debug_line = None

    def parse(self):
        try:
            rest = self.read_lines()
            first = next(rest)
            return parse_funcs(first, rest)
        except Exception as e:
            raise ParseError(f'{fileinput.filename()}:{fileinput.lineno()}: {self.debug_line}') from e

    def read_lines(self):
        for line in fileinput.input():
            line = line.strip()
            if not line:
                continue
            self.debug_line = line
            yield line


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
    while first.split()[0] == 'inputs':
        inputs = first.split()[1:]
        first = next(rest)

    blocks = parse_section(first, rest, parse_block)
    return Func(name, inputs, blocks)


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
    (op_str, *args) = expr.split()
    (op, size) = re.fullmatch(r'(.*?)(\d)?', op_str).groups()
    size = size and int(size)
    if op == 'asm':
        return parse_asm(first, rest, results, args)
    return Cmd(results, op, size, args)


def parse_asm(first, rest, results, args):
    first = next(rest)

    inputs = []
    clobbers = []
    if first.split()[0] == 'inputs':
        inputs = first.split()[1:]
        first = next(rest)
    if first.split()[0] == 'clobbers':
        clobbers =first.split()[1:]
        first = next(rest)

    instrs = parse_section(first, rest, parse_asm_instr)

    return Asm(results, 'asm', None, args, inputs, clobbers, instrs)


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


