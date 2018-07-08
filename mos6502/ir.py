import attr
from attr import attrs, attrib

# Actions


@attrs(cmp=False)
class Store(object):
    address = attrib()
    value = attrib()
    size = attrib()


# Operators


@attrs(cmp=False)
class NotEqual(object):
    size = attrib()
    lhs = attrib()
    rhs = attrib()


@attrs(cmp=False)
class Add(object):
    size = attrib()
    lhs = attrib()
    rhs = attrib()


@attrs(cmp=False)
class Call(object):
    destination = attrib()
    arguments = attrib()


@attrs(cmp=False)
class AsmCall(object):
    address = attrib()
    A = attrib()
    X = attrib()
    Y = attrib()


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


def blocks_dfs(start):
    blocks = []
    block = start
    while block not in blocks:
        blocks.append(block)
        if isinstance(block.terminator, Return):
            break
        block = block.terminator.destination
    return blocks


def print_blocks(start):
    print()
    blocks = blocks_dfs(start)
    block_ids = {block: i for i, block in enumerate(blocks)}

    def print_node(node, indent):
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
    print()


def replace(x, fn):
    try:
        for field in attr.fields(type(x)):
            setattr(x, field.name, replace(getattr(x, field.name), fn))
    except attr.exceptions.NotAnAttrsClassError:
        pass
    return fn(x)
