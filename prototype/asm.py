from attr import attrs, attrib


@attrs
class LoadImmediate(object):
    register = attrib()
    value = attrib()


# Note: This includes absolute zero page stores.
@attrs
class StoreAbsolute(object):
    register = attrib()
    address = attrib()


@attrs
class JumpSubroutine(object):
    address = attrib()


@attrs
class JumpAbsolute(object):
    destination = attrib()
