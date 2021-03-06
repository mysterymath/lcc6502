import attr
from attr import attrs, attrib

# Actions


@attrs(cmp=False)
class Store(object):
    size = attrib()
    address = attrib()
    value = attrib()


# Operators


@attrs(cmp=False)
class Add(object):
    size = attrib()
    lhs = attrib()
    rhs = attrib()


@attrs(cmp=False)
class Subtract(object):
    size = attrib()
    lhs = attrib()
    rhs = attrib()


@attrs(cmp=False)
class AsmCall(object):
    address = attrib()
    A = attrib()
    X = attrib()
    Y = attrib()


@attrs(cmp=False)
class Call(object):
    destination = attrib()
    arguments = attrib()


@attrs(cmp=False)
class Load(object):
    size = attrib()
    address = attrib()


@attrs(cmp=False)
class NotEqual(object):
    size = attrib()
    lhs = attrib()
    rhs = attrib()


@attrs(cmp=False)
class Truncate(object):
    size = attrib()
    value = attrib()


@attrs(cmp=False)
class ZeroExtend(object):
    size = attrib()
    value = attrib()


@attrs(cmp=False)
class SignExtend(object):
    size = attrib()
    value = attrib()


# Leaves


@attrs(cmp=False)
class Parameter(object):
    index = attrib()


@attrs(cmp=False)
class Local(object):
    index = attrib()


@attrs(cmp=False)
class Argument(object):
    value = attrib()


@attrs(cmp=False)
class Global(object):
    name = attrib()
    size = attrib()


@attrs(cmp=False)
class Constant(Global):
    value = attrib()


# Terminators


@attrs(cmp=False)
class Jump(object):
    destination = attrib()


@attrs(cmp=False)
class Branch(object):
    condition = attrib()
    true = attrib()
    false = attrib()


@attrs(cmp=False)
class Return(object):
    pass


# Composite nodes


@attrs(cmp=False)
class BasicBlock(object):
    instructions = attrib()

    @property
    def terminator(self):
        return self.instructions[-1]


@attrs(cmp=False)
class Function(object):
    name = attrib()
    start = attrib()


@attrs(cmp=False)
class Module(object):
    functions = attrib()
    globals_ = attrib()

    def print(self):
        print("# Functions")
        for function in self.functions:
            print("## {}:".format(function.name))
            print_blocks(function.start)

        print()
        print("# Globals")
        for global_ in self.globals_:
            print(global_)


def blocks_dfs(start):
    blocks = []
    work_list = [start]
    while work_list:
        block = work_list.pop()
        if block in blocks:
            continue
        blocks.append(block)

        if isinstance(block.terminator, Return):
            break
        elif isinstance(block.terminator, Branch):
            work_list += [block.terminator.false, block.terminator.true]
        else:
            work_list.append(block.terminator.destination)
    return blocks


def instructions_dfs(block):
    instructions = []
    for instruction in block.instructions:
        work_list = [instruction]
        while work_list:
            instruction = work_list.pop()
            if instruction in instructions:
                continue
            instructions.append(instruction)

            try:
                for field in attr.fields(type(instruction)):
                    work_list.append(getattr(instruction, field.name))
            except attr.exceptions.NotAnAttrsClassError:
                pass
    return instructions


def print_blocks(start):
    blocks = blocks_dfs(start)
    block_ids = {block: i for i, block in enumerate(blocks)}

    def print_node(node, indent):
        if isinstance(node, Function):
            print('  ' * indent + node.name)
            return
        if isinstance(node, BasicBlock):
            print('  ' * indent + "_{}".format(block_ids[node]))
            return

        try:
            fields = attr.fields(type(node))
            print('  ' * indent + type(node).__name__)
            indent += 1
            for field in fields:
                print('  ' * indent + field.name + ':')
                print_node(getattr(node, field.name), indent + 1)
        except attr.exceptions.NotAnAttrsClassError:
            print('  ' * indent + str(node))

    for block in blocks:
        print("_{}:".format(block_ids[block]))
        for instruction in block.instructions:
            print_node(instruction, indent=0)


def replace(x, fn):
    try:
        for field in attr.fields(type(x)):
            setattr(x, field.name, replace(getattr(x, field.name), fn))
    except attr.exceptions.NotAnAttrsClassError:
        pass
    return fn(x)
