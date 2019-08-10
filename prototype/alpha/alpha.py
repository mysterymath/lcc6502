from attr import attrs, attrib, Factory
import fileinput
import re


@attrs
class Block:
    name = attrib()
    cmds = attrib(default=Factory(list))

    def __str__(self):
        cmd_str = "\n".join(["  " + str(cmd) for cmd in self.cmds])
        return f'{self.name}\n{cmd_str}'


@attrs
class Cmd:
    result = attrib()
    op = attrib()
    args = attrib()

    def is_terminator(self):
        return self.op in ('br', 'ret')

    def __str__(self):
        result_str = f'{self.result} = ' if self.result else ''
        return f'{result_str}{self.op} {" ".join(self.args)}'


def parse_blocks():
    blocks = []
    block = None

    for line in fileinput.input():
        line = line.strip()
        if not line:
            continue

        if block is None:
            (block_name,) = line.split()
            block = Block(block_name)
        else:
            cmd = parse_cmd(line)
            block.cmds.append(cmd)
            if cmd.is_terminator():
                blocks.append(block)
                block = None

    return blocks


def parse_cmd(line):
    (result, rest) = re.fullmatch(r'(?:(\w) = )?(.*)', line).groups()
    (op, *args) = rest.split()
    return Cmd(result, op, args)


for block in parse_blocks():
    print(block)
