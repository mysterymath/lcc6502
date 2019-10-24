import fileinput
import re

from common import Func, Block, Cmd, Asm, AsmInstr


class ParseError(Exception):
    pass


def parse():
    return Parser(None).parse()

def parse_lines(inline):
    return Parser(inline).parse()

class Parser:
    def __init__(self, inline):
        self.debug_line = None
        self.inline = inline

    def parse(self):
        try:
            rest = self._read_lines()
            first = next(rest)
            return _parse_funcs(first, rest)
        except Exception as e:
            raise ParseError(f'{self._filename()}:{self._lineno()}: {self.debug_line}') from e

    def _filename(self):
        return 'inline' if self.inline else fileinput.filename()

    def _lineno(self):
        return self.lineno if self.inline else fileinput.lineno()

    def _read_lines(self):
        lines = self.inline.splitlines() if self.inline else fileinput.input()
        self.lineno = 0
        for line in lines:
            self.lineno += 1
            line = line.strip()
            if not line:
                continue
            self.debug_line = line
            yield line


def _parse_funcs(first, rest):
    funcs = []
    while True:
        funcs.append(_parse_func(first, rest))
        try:
            first = next(rest)
        except StopIteration:
            return funcs


def _parse_func(first, rest):
    (name,) = first.split()
    first = next(rest)

    inputs = []
    while first.split()[0] == 'inputs':
        inputs = first.split()[1:]
        first = next(rest)

    blocks = _parse_section(first, rest, _parse_block)
    return Func(name, inputs, blocks)


def _parse_block(first, rest):
    (name,) = first.split()
    first = next(rest)
    cmds = _parse_cmds(first, rest)
    return Block(name, cmds)


def _parse_cmds(first, rest):
    cmds = []
    while True:
        cmd = _parse_cmd(first, rest)
        cmds.append(cmd)
        if cmd.is_terminator():
            return cmds
        first = next(rest)


def _parse_cmd(first, rest):
    (results, expr) = re.fullmatch(r'(?:(.*) = )?(.*)', first).groups()
    results = results.split() if results else []
    (op_str, *args) = expr.split()
    (op, size) = re.fullmatch(r'(.*?)(\d)?', op_str).groups()
    size = size and int(size)
    if op == 'asm':
        return _parse_asm(first, rest, results, args)
    return Cmd(results, op, size, args)


def _parse_asm(first, rest, results, args):
    first = next(rest)

    inputs = []
    clobbers = []
    if first.split()[0] == 'inputs':
        inputs = first.split()[1:]
        first = next(rest)
    if first.split()[0] == 'clobbers':
        clobbers =first.split()[1:]
        first = next(rest)

    instrs = _parse_section(first, rest, _parse_asm_instr)

    return Asm(results, 'asm', None, args, inputs, clobbers, instrs)


def _parse_asm_instr(first, rest):
    (op, *args) = first.split()
    return AsmInstr(op, args)


def _parse_section(first, rest, _parse_item):
    items = []
    while True:
        items.append(_parse_item(first, rest))
        first = next(rest)
        if first == 'end':
            return items


