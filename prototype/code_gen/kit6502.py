from attr import attrs, attrib
from functools import reduce
from math import exp
from numbers import Number

import itertools
import random
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


@attrs(cmp=False)
class Var:
    size = attrib()
    name = attrib()


@attrs(cmp=False)
class Const(Var):
    value = attrib()


def live_locs(alloc, live_vars):
    locs = set()
    for var in live_vars:
        for loc in alloc[var]:
            if var.size == 2:
                assert isinstance(loc, Number)
                locs.add(loc)
                locs.add(loc + 1)
            else:
                locs.add(loc)
    return locs


def format_addr(addr):
    assert isinstance(addr, Number)
    if addr < 256:
        return addr
    return "bss+{}".format(addr - 256)


class Instruction:
    def gen(self, alloc, live_vars):
        self._gen(alloc, live_locs(alloc, live_vars))


def emit(*args, cost=2):
    asm.append([" ".join(str(arg) for arg in args), cost * 100**loop_number])


@attrs
class Add(Instruction):
    destination = attrib()
    left = attrib()
    right = attrib()

    def _gen(self, alloc, live):
        assert self.destination.size == 2
        assert self.left.size == 2
        assert self.right.size == 2
        assert len(alloc[self.destination]) == 1
        assert len(alloc[self.left]) == 1
        assert len(alloc[self.right]) <= 1

        for loc in itertools.chain(alloc[self.destination], alloc[self.left],
                                   alloc[self.right]):
            assert isinstance(loc, Number)

        if "Z" in live:
            emit("PHP", cost=3)

        if alloc[self.destination] == alloc[self.left] and isinstance(
                self.right, Const) and self.right.value == 1:
            (loc, ) = alloc[self.destination]
            label = new_label()

            emit("INC", loc, cost=5)
            emit("BNE", label)
            emit("INC", loc + 1, cost=5)
            emit("{}:".format(label), cost=0)
        else:
            (dest_loc, ) = alloc[self.destination]
            (left_loc, ) = alloc[self.left]
            (right_loc, ) = alloc[self.right] or (None, )
            dest_loc = format_addr(dest_loc)
            left_loc = format_addr(left_loc)
            right_loc = format_addr(right_loc)

            if "A" in live:
                emit("PHA", cost=3)

            emit("CLC")
            emit("LDA", left_loc, cost=3.5)
            if isinstance(self.right, Const):
                emit("ADC #{}".format(self.right.value % 256))
            else:
                emit("ADC {}".format(right_loc), cost=3.5)
            emit("STA", dest_loc, cost=3.5)
            emit("LDA {}+1".format(left_loc, cost=3.5))
            if isinstance(self.right, Const):
                emit("ADC #{}".format(self.right.value // 256))
            else:
                emit("ADC {}+1".format(right_loc), cost=3.5)
            emit("STA {}+1".format(dest_loc), cost=3.5)

            if "A" in live:
                emit("PLA", cost=4)

        if "Z" in live:
            emit("PLP", cost=4)


@attrs
class AsmCall(Instruction):
    address = attrib()
    args = attrib()
    clobber = attrib()

    def gen(self, alloc, live_vars):
        clobbered_vars = {
            var
            for var in live_vars if alloc[var] & self.clobber
        }
        clobbered_consts = {
            var
            for var in clobbered_vars if isinstance(var, Const)
        }
        clobbered_nonconsts = {
            var
            for var in clobbered_vars if not isinstance(var, Const)
        }
        clobbered_locs = live_locs(alloc, clobbered_nonconsts)

        if "Z" in clobbered_locs:
            emit("PHP", cost=3)
        if "A" in clobbered_locs:
            emit("PHA", cost=3)
        if "X" in clobbered_locs:
            emit("TXA")
            emit("PHA", cost=3)
        if "Y" in clobbered_locs:
            emit("TYA")
            emit("PHA", cost=3)

        cur_alloc = alloc.copy()
        cur_live_vars = live_vars.copy()
        for loc, var in self.args.items():
            assert var.size == 1
            dest = Var(1, "dest")
            cur_alloc[dest] = {loc}

            Mov(dest, var).gen(cur_alloc, cur_live_vars)
            cur_live_vars.add(dest)

        emit("JSR", self.address, cost=6)

        for const in clobbered_consts:
            LoadImm(var).gen({
                **alloc, var: alloc[var] & self.clobber
            }, live_vars - clobbered_nonconsts)

        if "Y" in clobbered_locs:
            emit("PLA", cost=4)
            emit("TAY")
        if "X" in clobbered_locs:
            emit("PLA", cost=4)
            emit("TAX")
        if "A" in clobbered_locs:
            emit("PLA", cost=4)
        if "Z" in clobbered_locs:
            emit("PLP", cost=4)


@attrs
class BrFalse(Instruction):
    condition = attrib()
    label = attrib()

    def _gen(self, alloc, live):
        assert self.condition.size == 0
        assert not isinstance(self.condition, Const)
        assert "Z" not in live
        dest = Var(0, "dest")
        Mov(dest, self.condition)._gen({**alloc, dest: {"Z"}}, live)
        emit("BEQ", self.label)


@attrs
class Load(Instruction):
    destination = attrib()
    address = attrib()
    offset = attrib()
    zero = attrib(default=None, kw_only=True)

    def _gen(self, alloc, live):
        assert self.destination.size == 1
        assert self.address.size == 2
        assert not isinstance(self.address, Const)
        assert isinstance(self.offset, Const)

        assert all(isinstance(addr, Number) for addr in alloc[self.address])
        addr = next((addr for addr in alloc[self.address] if addr < 256), None)

        # TODO: Fix
        assert "Z" not in live
        assert "A" not in live

        if addr is None:
            for loc in range(128, 255):
                if loc not in live and loc + 1 not in live:
                    addr = loc
                    break
            assert addr is not None
            zp_addr = Var(2, "zp_addr")
            Mov(zp_addr, self.address)._gen({**alloc, zp_addr: {addr}}, live)

        if "Y" not in alloc[self.offset]:
            LoadImm(self.offset)._gen({
                **alloc, self.offset: {"Y"}
            }, live | {addr})

        emit("LDA ({}),Y".format(addr), cost=5)

        a_var = Var(1, "a_var")
        Mov(self.destination, a_var)._gen({
            **alloc, a_var: {"A"}
        }, live | {"Z"})

        if self.zero:
            z_var = Var(1, "z_var")
            Mov(self.zero, z_var)._gen({
                **alloc, z_var: {"Z"}
            }, live | alloc[self.destination])

        #need_to_save_a = False

        #if not self.zero:
        #    emit("PHP")
        #if "A" in live:
        #    need_to_save_a = True
        #    emit("PHA")
        #if "Y" in live and "Y" not in alloc[self.offset]:
        #    need_to_save_a = True
        #    emit("TYA")
        #    emit("PHA")

        #is_saved = False
        #if addr is None:
        #    for loc in range(128, 255):
        #        if loc not in live and loc+1 not in live:
        #            addr = loc
        #            break
        #    if addr is None:
        #        emit("LDA 128")
        #        emit("PHA")
        #        emit("LDA 129")
        #        emit("PHA")
        #        addr = 128
        #        is_saved = True
        #    dest = Var(2, "dest")
        #    Mov(dest, self.address)._gen({**alloc, dest: {addr}}, live)

        #assert addr is not None
        #assert isinstance(addr, Number)
        #assert addr < 256

        #if "Y" not in alloc[self.offset]:
        #    LoadImm(self.offset)._gen({**alloc, self.offset: {"Y"}}, live - {"A", "Y", "Z", addr, addr + 1})

        #if need_to_save_a:
        #    if is_saved:
        #        tmp = 128
        #    else:
        #        tmp = next(loc for loc in itertools.count(128) if loc not in live)
        #    tmp = format_addr(tmp)
        #    emit("STA", tmp)

        #if is_saved:
        #    emit("PLA")
        #    emit("STA 128")
        #    emit("PLA")
        #    emit("STA 129")

        #if "Y" in live and "Y" not in alloc[self.offset]:
        #    emit("PLA")
        #    emit("TAY")

        #if need_to_save_a:
        #    emit("LDA", tmp)
        #    tmp_var = Var(1, "tmp_var")
        #    Mov(self.destination, tmp_var)._gen({**alloc, tmp_var: {"A"}}, live | {"Z"})

        ## TODO: This function is simply unfinished!

        #z_var = Var(0, "z_var")
        #Mov(self.zero, z_var)._gen({**alloc, z_var: {"Z"}}, live | alloc[self.destination])

        #if "A" in live:
        #    # TODO: Don't clobber Z when restoring A.
        #    assert self.zero is None
        #    emit("PLA")

        #if not self.zero:
        #    emit("PLP")


@attrs
class LoadImm(Instruction):
    value = attrib()

    def _gen(self, alloc, live):
        assert isinstance(self.value, Const)
        if not alloc[self.value]:
            return

        if self.value.size == 2:
            new_alloc = alloc.copy()
            del new_alloc[self.value]

            lo = Const(1, "LO", "<{}".format(self.value.value))
            hi = Const(1, "HI", ">{}".format(self.value.value))
            new_alloc[lo] = set()
            new_alloc[hi] = set()

            for loc in alloc[self.value]:
                assert isinstance(loc, Number)
                new_alloc[lo].add(loc)
                new_alloc[hi].add(loc + 1)

            LoadImm(lo)._gen(new_alloc, live)
            LoadImm(hi)._gen(new_alloc, live | new_alloc[lo])
            return

        assert self.value.size == 1

        if "Z" in live:
            emit("PHP", cost=3)

        locs = alloc[self.value]
        addrs = set(filter(lambda loc: isinstance(loc, Number), locs))
        if "A" in locs:
            emit("LDA #{}".format(self.value.value), cost=3.5)
        if "X" in locs:
            emit("LDX #{}".format(self.value.value), cost=3.5)
        if "Y" in locs:
            emit("LDY #{}".format(self.value.value), cost=3.5)

        for addr in addrs:
            addr = format_addr(addr)
            new_alloc = alloc.copy()
            new_alloc[self.value] = locs - addrs
            address = Const(2, "addr", addr)
            new_alloc[address] = set()
            Store(address, self.value)._gen(new_alloc, live)

        if "Z" in live:
            emit("PLP", cost=4)


@attrs
class Mov(Instruction):
    destination = attrib()
    source = attrib()

    def _gen(self, alloc, live):
        assert self.destination.size == self.source.size or self.destination.size <= 1 and self.source.size <= 1
        assert not isinstance(self.destination, Const)

        new_locs = alloc[self.destination]
        locs = alloc[self.source].copy()
        if new_locs.issubset(locs):
            return

        if isinstance(self.source, Const):
            new_const = Const(self.destination.size, "new_const",
                              self.source.value)
            LoadImm(new_const)._gen({
                **alloc, new_const: alloc[self.destination]
            }, live)
            return

        if self.destination.size == 2:
            new_alloc = alloc.copy()
            lo_dest = Var(1, "lo_dest")
            hi_dest = Var(1, "hi_dest")
            lo_source = Var(1, "lo_source")
            hi_source = Var(1, "hi_source")
            new_alloc[lo_dest] = set()
            new_alloc[hi_dest] = set()
            new_alloc[lo_source] = set()
            new_alloc[hi_source] = set()

            for loc in alloc[self.destination]:
                assert isinstance(loc, Number)
                new_alloc[lo_dest].add(loc)
                new_alloc[hi_dest].add(loc + 1)

            for loc in alloc[self.source]:
                assert isinstance(loc, Number)
                new_alloc[lo_source].add(loc)
                new_alloc[hi_source].add(loc + 1)

            Mov(lo_dest, lo_source)._gen(new_alloc,
                                         live | new_alloc[hi_source])
            Mov(hi_dest, hi_source)._gen(new_alloc, live | new_alloc[lo_dest])
            return

        assert self.destination.size <= 1

        saved_a = False

        if "Z" in live:
            emit("PHP", cost=3)

        def z_to(reg):
            flag_set = new_label()
            end = new_label()
            emit("BEQ", flag_set)
            emit("LD{} #0".format(reg))
            emit("BNE", end)
            emit("{}:".format(flag_set))
            emit("LD{} #1".format(reg))
            emit("{}:".format(end))

        if "A" in new_locs and "A" not in locs:
            if "X" in locs:
                emit("TXA")
            elif "Y" in locs:
                emit("TYA")
            elif any(isinstance(addr, Number) for addr in locs):
                addr = next((addr for addr in locs
                             if isinstance(addr, Number) and addr < 256), None)
                if addr is None:
                    addr = next((format_addr(addr) for addr in locs
                                 if isinstance(addr, Number)), None)
                assert addr is not None
                emit("LDA", addr, cost=3.5)
            else:
                assert "Z" in locs
                z_to("A")
            locs.add("A")
            locs.add("Z")

        if "X" in new_locs and "X" not in locs:
            if "A" in locs:
                emit("TAX")
            elif "Y" in locs:
                if "A" in live and not saved_a:
                    emit("PHA", cost=3)
                    saved_a = True
                locs.add("A")
                emit("TYA")
                emit("TAX")
            elif any(isinstance(addr, Number) for addr in locs):
                addr = next((addr for addr in locs
                             if isinstance(addr, Number) and addr < 256), None)
                if addr is None:
                    addr = next((format_addr(addr) for addr in locs
                                 if isinstance(addr, Number)), None)
                assert addr is not None
                emit("LDX", addr, cost=3.5)
            else:
                assert "Z" in locs
                z_to("X")
            locs.add("X")
            locs.add("Z")

        if "Y" in new_locs and "Y" not in locs:
            if "A" in locs:
                emit("TAY")
            elif "X" in locs:
                if "A" in live and not saved_a:
                    emit("PHA", cost=3)
                    saved_a = True
                locs.add("A")
                emit("TXA")
                emit("TAY")
            elif any(isinstance(addr, Number) for addr in locs):
                addr = next((addr for addr in locs
                             if isinstance(addr, Number) and addr < 256), None)
                if addr is None:
                    addr = next((format_addr(addr) for addr in locs
                                 if isinstance(addr, Number)), None)
                assert addr is not None
                emit("LDY", addr, cost=3.5)
            else:
                assert "Z" in locs
                z_to("Y")
            locs.add("Y")
            locs.add("Z")

        for addr in new_locs:
            if not isinstance(addr, Number):
                continue
            addr = format_addr(addr)
            if "A" in locs:
                loc = "A"
            elif "X" in locs:
                loc = "X"
            elif "Y" in locs:
                loc = "Y"
            else:
                if "A" in live and not saved_a:
                    emit("PHA", cost=3)
                    saved_a = True
                tmp = Var(1, "tmp")
                Mov(tmp, self.source)._gen({**alloc, tmp: {"A"}}, live)
                locs.add("A")
                locs.add("Z")
                loc = "A"
            emit("ST{} {}".format(loc, addr))

        if saved_a:
            emit("PLA", cost=4)
            if "A" in alloc[self.source]:
                locs.add("A")
                locs.add("Z")
            else:
                locs.remove("A")
                locs.remove("Z")

        if "Z" in new_locs and "Z" not in locs:
            if "A" in locs:
                emit("CMP #0")
            elif "X" in locs:
                emit("CPX #0")
            elif "Y" in locs:
                emit("CPY #0")
            else:
                addr = next((addr for addr in locs
                             if isinstance(addr, Number) and addr < 256), None)
                if not addr:
                    addr = next((format_addr(addr) for addr in locs
                                 if isinstance(addr, Number)), None)
                assert addr is not None
                if "A" not in live:
                    emit("LDA", addr, cost=3.5)
                elif "X" not in live:
                    emit("LDX", addr, cost=3.5)
                elif "Y" not in live:
                    emit("LDY", addr, cost=3.5)
                else:
                    emit("INC", addr, cost=5)
                    emit("DEC", addr, cost=5)
        elif "Z" in live:
            emit("PLP", cost=4)


@attrs
class Store(Instruction):
    address = attrib()
    value = attrib()

    def _gen(self, alloc, live):
        assert not alloc[self.address]
        assert self.address.size == 2
        assert self.value.size == 1

        if "A" in alloc[self.value]:
            emit("STA", self.address.value, cost=3.5)
        elif "X" in alloc[self.value]:
            emit("STX", self.address.value, cost=3.5)
        elif "Y" in alloc[self.value]:
            emit("STY", self.address.value, cost=3.5)
        else:
            if "A" in live:
                if "Z" in live:
                    emit("PHP", cost=3)
                emit("PHA", cost=3)
                self._gen(alloc, live - {"A", "Z"})
                emit("PLA", cost=4)
                if "Z" in live:
                    emit("PLP", cost=4)
                return
            dest = Var(1, "dest")
            new_alloc = {**alloc, dest: {"A"}}
            Mov(dest, self.value)._gen(new_alloc, live)
            Store(self.address, dest)._gen(new_alloc, live)


strings = []

next_label = 1


def new_label():
    global next_label
    label = "__{}".format(next_label)
    next_label += 1
    return label


def string(name, value):
    strings.append((name, value))
    return Const(2, name, name)


PUT_CHARACTERS = Const(1, "PUT_CHARACTERS", 0x0B)
IOCB0 = 0x0340
ICCMD = 2
ICBLL = 8
ICBLH = 9
ZERO = Const(1, "ZERO", 0)
ONE = Const(2, "ONE", 1)
IOCB0_ICCMD = Const(2, "IOCB0_ICCMD", IOCB0 + ICCMD)
IOCB0_ICBLL = Const(2, "IOCB0_ICBLL", IOCB0 + ICBLL)
IOCB0_ICBLH = Const(2, "IOCB0_ICBLH", IOCB0 + ICBLH)
CIOV = 0xE456
kHello = string("kHello", "Hello, world!")
ptr = Var(2, "ptr")
char = Var(1, "char")
done = Var(0, "done")

alloc = {
    PUT_CHARACTERS: set(),
    IOCB0_ICCMD: set(),
    IOCB0_ICBLL: set(),
    IOCB0_ICBLH: set(),
    ZERO: set(),
    ONE: set(),
    kHello: {256},
    ptr: {258},
    char: {260},
    done: {261}
}

#alloc = {
#    PUT_CHARACTERS: set(),
#    IOCB0_ICCMD: set(),
#    IOCB0_ICBLL: set(),
#    IOCB0_ICBLH: set(),
#    ZERO: {"X", "Y"},
#    ONE: set(),
#    kHello: {128},
#    ptr: {128},
#    char: {"A"},
#    done: {"Z"}
#}

interference = {
    PUT_CHARACTERS: {
        IOCB0_ICCMD,
        IOCB0_ICBLL,
        IOCB0_ICBLH,
        ZERO,
        ONE,
        kHello,
    },
    IOCB0_ICCMD: {
        PUT_CHARACTERS,
        IOCB0_ICBLL,
        IOCB0_ICBLH,
        ZERO,
        ONE,
        kHello,
    },
    IOCB0_ICBLL: {
        PUT_CHARACTERS,
        IOCB0_ICCMD,
        IOCB0_ICBLH,
        ZERO,
        ONE,
        kHello,
    },
    IOCB0_ICBLH: {
        PUT_CHARACTERS,
        IOCB0_ICCMD,
        IOCB0_ICBLL,
        ZERO,
        ONE,
        kHello,
    },
    ZERO: {
        PUT_CHARACTERS,
        IOCB0_ICCMD,
        IOCB0_ICBLL,
        IOCB0_ICBLH,
        ONE,
        kHello,
        ptr,
        char,
        done,
    },
    ONE: {
        PUT_CHARACTERS,
        IOCB0_ICCMD,
        IOCB0_ICBLL,
        IOCB0_ICBLH,
        ZERO,
        kHello,
        ptr,
        char,
        done,
    },
    kHello: {
        PUT_CHARACTERS,
        IOCB0_ICCMD,
        IOCB0_ICBLL,
        IOCB0_ICBLH,
        ZERO,
        ONE,
    },
    ptr: {ZERO, ONE, char, done},
    char: {ZERO, ONE, ptr, done},
    done: {ZERO, ONE, ptr, char}
}

# Assert interference relation is symmetric
for a in interference:
    for b in interference[a]:
        assert a in interference[b], "{} {}".format(a, b)


def attempt(alloc):
    global asm
    global loop_number
    asm = []
    loop_number = 0
    emit(".word $FFFF")
    emit("start = $0700")
    emit()
    emit(".word start")
    emit(".word bss - 1")
    emit("* = start")

    LoadImm(PUT_CHARACTERS).gen(alloc, {})
    LoadImm(IOCB0_ICCMD).gen(alloc, {PUT_CHARACTERS})
    LoadImm(IOCB0_ICBLL).gen(alloc, {PUT_CHARACTERS, IOCB0_ICCMD})
    LoadImm(IOCB0_ICBLH).gen(alloc, {PUT_CHARACTERS, IOCB0_ICCMD, IOCB0_ICBLL})
    LoadImm(ZERO).gen(alloc,
                      {PUT_CHARACTERS, IOCB0_ICCMD, IOCB0_ICBLL, IOCB0_ICBLH})
    LoadImm(ONE).gen(
        alloc, {PUT_CHARACTERS, IOCB0_ICCMD, IOCB0_ICBLL, IOCB0_ICBLH, ZERO})
    LoadImm(kHello).gen(
        alloc,
        {PUT_CHARACTERS, IOCB0_ICCMD, IOCB0_ICBLL, IOCB0_ICBLH, ZERO, ONE})
    Store(IOCB0_ICCMD, PUT_CHARACTERS).gen(
        alloc, {IOCB0_ICBLL, IOCB0_ICBLH, ZERO, ONE, kHello})
    Store(IOCB0_ICBLL, ZERO).gen(alloc, {IOCB0_ICBLH, ZERO, ONE, kHello})
    Store(IOCB0_ICBLH, ZERO).gen(alloc, {ZERO, ONE, kHello})
    Mov(ptr, kHello).gen(alloc, {ZERO, ONE})
    loop = new_label()
    emit("{}:".format(loop))
    loop_number += 1
    Load(char, ptr, ZERO, zero=done).gen(alloc, {ZERO, ONE, ptr})
    BrFalse(done, "__end").gen(alloc, {ZERO, ONE, ptr, char})
    AsmCall(CIOV, {
        "A": char,
        "X": ZERO
    }, {"Y", "Z"}).gen(alloc, {ZERO, ONE, ptr})
    Add(ptr, ptr, ONE).gen(alloc, {ZERO, ONE, ptr})
    emit("JMP", loop)
    loop_number -= 1

    emit("__end JMP __end")
    for name, value in strings:
        emit('{} .byt "{}",0'.format(name, value))

    emit("bss = *")
    return asm


def interferes(var, loc):
    for other in interference[var]:
        # First bytes interfere
        if loc in alloc[other]:
            return True
        # Last byte of var interferes with first byte of other
        if var.size == 2:
            assert isinstance(loc, Number)
            if loc + 1 in alloc[other]:
                return True
        # First byte of var interferes with last byte of other
        if other.size == 2:
            for other_loc in alloc[other]:
                assert isinstance(other_loc, Number)
                if loc == other_loc + 1:
                    return True
        # For last and last, this implies first and first, which is handled above.
    return False


def get_neighborhood(alloc):
    neighborhood = []

    # TODO: Disallow 255 from being allocated to a 2-byte value.
    max_zp = max(
        (loc for var in alloc for loc in alloc[var]
         if isinstance(loc, Number) and loc < 256),
        default=127)
    max_mem = max(
        (loc for var in alloc for loc in alloc[var]
         if isinstance(loc, Number)),
        default=255)

    for var in alloc:
        # Remove a location
        if isinstance(var, Const) or len(alloc[var]) > 1:
            for loc in alloc[var]:
                neighborhood.append({**alloc, var: alloc[var] - {loc}})

        if var.size == 0 and "Z" not in alloc[var] and not interferes(
                var, "Z"):
            neighborhood.append({**alloc, var: {*alloc[var], "Z"}})
            neighborhood.append({**alloc, var: {"Z"}})

        if var.size <= 1 and "A" not in alloc[var] and not interferes(
                var, "A"):
            neighborhood.append({**alloc, var: {*alloc[var], "A"}})
            neighborhood.append({**alloc, var: {"A"}})
        if var.size <= 1 and "X" not in alloc[var] and not interferes(
                var, "X"):
            neighborhood.append({**alloc, var: {*alloc[var], "X"}})
            neighborhood.append({**alloc, var: {"X"}})
        if var.size <= 1 and "Y" not in alloc[var] and not interferes(
                var, "Y"):
            neighborhood.append({**alloc, var: {*alloc[var], "Y"}})
            neighborhood.append({**alloc, var: {"Y"}})
        for loc in range(128, max_zp + 2):
            if interferes(var, loc):
                continue
            neighborhood.append({**alloc, var: {*alloc[var], loc}})
            neighborhood.append({**alloc, var: {loc}})
        for loc in range(256, max_mem + 2):
            if interferes(var, loc):
                continue
            neighborhood.append({**alloc, var: {*alloc[var], loc}})
    return neighborhood


def asm_cost(asm):
    return sum(cost for _, cost in asm)


cost = asm_cost(attempt(alloc))
best_alloc = alloc
best_cost = cost

anneal = False
if anneal:
    eprint("Annealing:")
    temp = 1.25
    eprint("Temp:", temp)
    num_iter = 0
    num_accepted = 0
    while True:
        if cost < best_cost:
            best_cost = cost
            best_alloc = alloc
        eprint(cost)
        num_iter += 1
        if num_accepted >= 10 * len(alloc):
            temp *= 0.9
            eprint("Temp:", temp)
            num_accepted = 0
            num_iter = 0
        if num_iter >= 1000 * len(alloc):
            break  # Frozen
        new_alloc = random.choice(get_neighborhood(alloc))
        try:
            new_cost = asm_cost(attempt(new_alloc))
        except:
            continue
        if new_cost <= cost or random.random() < exp((cost - new_cost) / temp):
            if new_cost != cost:
                num_accepted += 1
            cost = new_cost
            alloc = new_alloc

hill_climb = True
if hill_climb:
    eprint("Hill Climbing:")
    while True:
        eprint(best_cost)
        for new_alloc in get_neighborhood(alloc):
            try:
                cost = asm_cost(attempt(new_alloc))
            except:
                continue
            if cost < best_cost:
                best_alloc = new_alloc
                best_cost = cost

        if best_alloc is alloc:
            break

        alloc = best_alloc

eprint(best_alloc)
print("\n".join(stmt for stmt, _ in attempt(best_alloc)))
