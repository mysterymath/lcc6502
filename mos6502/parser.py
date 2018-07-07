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
                size = match[3] and int(match[3])

                if operation == 'CNST':
                    instructions.append(int(components[1]))
                elif operation == 'ASGN':
                    value = instructions.pop()
                    address = instructions.pop()
                    # Assignments to formal parameters are not yet handled.
                    if not isinstance(address, ir.Parameter):
                        if not size:
                            raise ParseError(
                                "ASGN requires a size; found none.")
                        instructions.append(ir.Store(address, value, size))
                elif operation == 'LABEL':
                    block = resolve_block(components[1])
                    if instructions is not None:
                        instructions.append(ir.Jump(block))
                    instructions = block.instructions
                elif operation == 'ADDRF':
                    instructions.append(ir.Parameter(int(components[1])))
                elif operation == 'ADDRG':
                    instructions.append(components[1])
                elif operation == 'JUMP':
                    label = instructions.pop()
                    instructions.append(ir.Jump(resolve_block(label)))
                    block = None
                    instructions = None
                elif operation == 'INDIR':
                    pass
                elif operation == 'ARG':
                    instructions.append(ir.Argument(instructions.pop()))
                elif operation.startswith('CV'):
                    pass
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
                else:
                    raise ParseError(
                        "Unsupported operation: {}".format(operation))

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
