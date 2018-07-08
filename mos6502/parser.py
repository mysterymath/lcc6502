import re
import sys
from numbers import Number

import ir


class ParseError(Exception):
    pass


def parse():
    labels = {}
    line = None

    def advance():
        nonlocal line
        line = sys.stdin.readline().strip()

    def resolve_block(label):
        if label not in labels:
            labels[label] = ir.BasicBlock([])
        return labels[label]

    def resolve_function(label):
        if label not in labels:
            labels[label] = ir.Function(label, ir.BasicBlock([]))
        return labels[label]

    def parse_function():
        name = line.split()[1]

        block = resolve_function(name).start
        instructions = block.instructions
        advance()

        try:
            while not line.startswith("endproc"):
                if not line:
                    raise ParseError(
                        "Expected: 'endproc {}...'. Found: EOF".format(name))
                components = line.split()
                match = re.match("(\w+)(\D)(\d)?", components[0])
                operation = match[1]
                type_ = match[2]
                size = match[3] and int(match[3])
                try:
                    argument = components[1]
                except IndexError:
                    pass

                # 0 children
                if operation == 'ADDRF':
                    instructions.append(ir.Parameter(int(argument)))
                elif operation == 'ADDRG':
                    instructions.append(argument)
                elif operation == 'ADDRL':
                    instructions.append(ir.Local(int(argument)))
                elif operation == 'CNST':
                    instructions.append(int(argument))
                # 1 child
                elif operation == 'CVU' or operation == 'CVI':
                    target_size = size
                    source_size = int(argument)

                    if type_ not in 'UI':
                        raise ParseError(
                            "Could not parse conversion: {}".format(line))

                    if target_size < source_size:
                        instructions.append(
                            ir.Truncate(target_size, instructions.pop()))
                    elif target_size > source_size:
                        if type_ == 'U':
                            instructions.append(
                                ir.ZeroExtend(target_size, instructions.pop()))
                        else:
                            instructions.append(
                                ir.SignExtend(target_size, instructions.pop()))
                elif operation == 'INDIR':
                    instructions.append(ir.Load(size, instructions.pop()))
                # 2 children
                elif operation == 'ADD':
                    lhs = instructions.pop()
                    rhs = instructions.pop()
                    instructions.append(ir.Add(size, lhs, rhs))
                elif operation == 'ARG':
                    instructions.append(ir.Argument(instructions.pop()))
                elif operation == 'ASGN':
                    value = instructions.pop()
                    address = instructions.pop()
                    instructions.append(ir.Store(size, address, value))
                elif operation == 'CALL':
                    label = instructions.pop()

                    arguments = []
                    while instructions and isinstance(instructions[-1],
                                                      ir.Argument):
                        arguments.append(instructions.pop().value)
                    arguments.reverse()

                    if label == '__asm_call':

                        def ArgFn(arg):
                            if not isinstance(arg, Number):
                                return arg
                            if arg >= 0:
                                return arg

                        instructions.append(
                            ir.AsmCall(arguments[0],
                                       *map(ArgFn, arguments[1:])))
                    else:
                        if label not in labels:
                            labels[label] = ir.Function(
                                label, ir.BasicBlock([]))
                        instructions.append(ir.Call(labels[label], arguments))
                elif operation == 'JUMP':
                    label = instructions.pop()
                    instructions.append(ir.Jump(resolve_block(label)))
                    block = None
                    instructions = None
                elif operation == 'LABEL':
                    block = resolve_block(argument)
                    if instructions is not None:
                        instructions.append(ir.Jump(block))
                    instructions = block.instructions
                elif operation == 'NE':
                    lhs = instructions.pop()
                    rhs = instructions.pop()
                    true = resolve_block(argument)
                    false = ir.BasicBlock([])
                    instructions.append(
                        ir.Branch(ir.NotEqual(size, lhs, rhs), true, false))
                    block = false
                    instructions = block.instructions
                else:
                    raise ParseError("Unsupported operation: {}".format(line))

                advance()
        except ParseError as e:
            raise ParseError("Could not parse function {}".format(name)) from e
        advance()

        # If the block does not already have a terminator, add a Return.
        if not instructions or not isinstance(block.terminator, ir.Jump):
            instructions.append(ir.Return())

    advance()

    while line:
        if line.startswith("proc"):
            parse_function()
        else:
            advance()

    return {v for v in labels.values() if isinstance(v, ir.Function)}
