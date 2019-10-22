from collections import defaultdict, Counter
import copy
import itertools

from common import Func, Block, Cmd, Asm, AsmInstr
from common import collect_predecessors, remove_copies
from parse import parse
from to_ssa import to_ssa


def compute_live_sets(func):
    defns = get_definitions(func)
    for block in func.blocks:
        block.live_in = set()
        block.live_out = set()

    preds = collect_predecessors(func.blocks)

    is_done = False
    while not is_done:
        is_done = True
        for block in func.blocks:
            live = block.live_out.copy()
            for cmd in reversed(block.cmds):
                live -= set(cmd.results)
                if cmd.op != 'phi':
                    live |= set(cmd.args) & defns
            block.live_in = live.copy()

            for pred in preds[block.name]:
                old_size = len(pred.live_out)

                pred.live_out |= block.live_in
                for cmd in block.cmds:
                    if cmd.op != 'phi':
                        continue
                    for a_block, a in zip(cmd.args[::2], cmd.args[1::2]):
                        if a_block == pred.name:
                            pred.live_out |= {a} & defns

                if len(pred.live_out) != old_size:
                    is_done = False


def break_live_ranges_across_recursive_calls(funcs):
    callers = defaultdict(set)
    for func in funcs:
        for block in func.blocks:
            for cmd in block.cmds:
                if cmd.op == 'call':
                    callers[cmd.args[0]].add(func.name)

    def callers_size():
        return sum(len(v) for v in callers.values())

    while True:
        old_size = callers_size()
        for lers in callers.values():
            new_lers = set()
            for ler in lers:
                # Never add anything to the callers defaultdict, since it is
                # being iterated.
                if ler in callers:
                    new_lers |= callers[ler]
            lers |= new_lers
        if callers_size() == old_size:
            break

    for func in funcs:
        defns = get_definitions(func)
        still_in_ssa = True
        for block in func.blocks:
            new_cmds = []
            live = block.live_out.copy()
            for cmd in reversed(block.cmds):
                if cmd.op == 'call' and cmd.args[0] in callers[func.name]:
                    live_across = live.copy()
                    live_across -= set(cmd.results)
                    if live_across:
                        still_in_ssa = False
                        live_across = list(live_across)
                        # Note that new_cmds is in reverse order
                        new_cmds.append(Cmd(live_across, 'restore', None, []))
                        new_cmds.append(cmd)
                        new_cmds.append(Cmd([], 'save', None, live_across))
                    else:
                        new_cmds.append(cmd)
                    # No values are live across recursive call, so only args of
                    # call are now live before the call.
                    live = set(cmd.args) & defns
                else:
                    new_cmds.append(cmd)
                    live -= set(cmd.results)
                    live |= set(cmd.args) & defns
            new_cmds.reverse()
            block.cmds = new_cmds

        if not still_in_ssa:
            to_ssa(func.blocks)


def get_definitions(func):
    defns = set(func.inputs)
    for block in func.blocks:
        for cmd in block.cmds:
            defns |= set(cmd.results)
    return defns


def merge_all_funcs(funcs):
    for func in funcs:
        names = get_definitions(func)
        for block in func.blocks:
            names.add(block.name)

        def new_name(name):
            if name == '_':
                return name
            elif name == 'start':
                return func.name
            elif name in names:
                return f'{func.name}_{name}'
            else:
                return name

        for block in func.blocks:
            block.name = new_name(block.name)
            for cmd in block.cmds:
                cmd.results = list(map(new_name, cmd.results))
                cmd.args = list(map(new_name, cmd.args))

    funcs_by_name = {}
    for func in funcs:
        funcs_by_name[func.name] = func

    for func in funcs:
        for block in func.blocks:
            cmds = []
            for cmd in block.cmds:
                if cmd.op == 'call':
                    callee = cmd.args[0]
                    inputs = funcs_by_name[callee].inputs
                    for i, arg in enumerate(cmd.args[1:]):
                        input_name = f'{callee}_{inputs[i]}'
                        cmds.append(Cmd([input_name], 'copy', None, [arg]))

                    cmds.append(Cmd([], 'jsr', None, [callee]))

                    for i, result in enumerate(cmd.results):
                        if result != '_':
                            cmds.append(Cmd([result], 'copy', None, [f'__{callee}_o{i+1}']))
                elif cmd.op == 'ret':
                    for i, arg in enumerate(cmd.args):
                        cmds.append(Cmd([f'__{func.name}_o{i+1}'], 'copy', None, [arg]))
                    cmds.append(Cmd([], 'rts', None, [func.name]))
                else:
                    cmds.append(cmd)
            block.cmds = cmds

    block_names = set(block.name for func in funcs for block in func.blocks)
    def new_block_name(name):
        for i in itertools.chain([''], itertools.count(1)):
            candidate = f'{name}{i}'
            if candidate not in block_names:
                block_names.add(candidate)
                return candidate

    blocks = []
    rts_dest_blocks = defaultdict(set)
    phi_blocks = defaultdict(set)
    for func in funcs:
        for block in func.blocks:
            block_name = block.name
            cmds = []
            for cmd in block.cmds:
                cmds.append(cmd)
                if cmd.op == 'jsr':
                    block.cmds = cmds
                    blocks.append(block)

                    block = Block(new_block_name(block_name), [])
                    cmd.args.append(block.name)
                    cmds = []
                    rts_dest_blocks[cmd.args[0]].add(block.name)
            phi_blocks[block_name] = block.name
            block.cmds = cmds
            blocks.append(block)

    for block in blocks:
        for cmd in block.cmds:
            if cmd.op == 'rts':
                (callee,) = cmd.args
                cmd.args = list(rts_dest_blocks[callee])
            elif cmd.op == 'phi':
                for i in range(0, len(cmd.args), 2):
                    cmd.args[i] = phi_blocks[cmd.args[i]]
    return blocks


def lower_cmp(blocks):
    defns = get_blocks_definitions(blocks)

    for block in blocks:
        cmds = []

        for cmd in block.cmds:
            if cmd.op == 'lt':
                t = new_name('t', defns)
                cmds.append(Cmd([t], 'ge', cmd.size, [cmd.args[0], cmd.args[1]]))
                cmds.append(Cmd(cmd.results, 'not', None, [t]))
            elif cmd.op == 'le':
                cmds.append(Cmd(cmd.results, 'ge', cmd.size, [cmd.args[1], cmd.args[0]]))
            elif cmd.op == 'gt':
                t = new_name('t', defns)
                cmds.append(Cmd([t], 'ge', cmd.size, [cmd.args[1], cmd.args[0]]))
                cmds.append(Cmd(cmd.results, 'not', None, [t]))
            elif cmd.op == 'ne':
                t = new_name('t', defns)
                cmds.append(Cmd([t], 'eq', cmd.size, [cmd.args[0], cmd.args[1]]))
                cmds.append(Cmd(cmd.results, 'not', None, [t]))
            else:
                cmds.append(cmd)
        block.cmds = cmds


def lower_16(blocks):
    defns = get_blocks_definitions(blocks)

    split_vars = {}

    def split(var):
        if var == 'main_i1_lo':
            breakpoint()
        if var in split_vars:
            return split_vars[var]
        if var not in defns:
            var = int(var, 0)
            s = [str(var & 0xff), str((var >> 8) & 0xff)]
        else:
            s = [
                new_name(var + '_lo', defns),
                new_name(var + '_hi', defns),
            ]
        split_vars[var] = s
        return s

    fixed = False
    while not fixed:
        fixed = True
        for block in blocks:
            cmds = []

            for cmd in block.cmds:
                if cmd.size is None and cmd.op != 'split':
                    cmds.append(cmd)
                    continue

                if cmd.op == 'add':
                    assert cmd.size in (1, 2)
                    if cmd.size == 1:
                        cmds.append(Cmd(cmd.results, 'adc', None, cmd.args + ['0']))
                    else:
                        (result,) = cmd.results

                        arg1_lo, arg1_hi = split(cmd.args[0])
                        arg2_lo, arg2_hi = split(cmd.args[1])
                        result_lo, result_hi = split(result)
                        carry = new_name('carry', defns)

                        cmds.append(Cmd([result_lo, carry], 'adc', None, [arg1_lo, arg2_lo, '0']))
                        cmds.append(Cmd([result_hi, '_'], 'adc', None, [arg1_hi, arg2_hi, carry]))
                elif cmd.op == 'sub':
                    assert cmd.size in (1, 2)
                    if cmd.size == 1:
                        cmds.append(Cmd(cmd.results, 'sbc', None, cmd.args + ['1']))
                    else:
                        (result,) = cmd.results

                        arg1_lo, arg1_hi = split(cmd.args[0])
                        arg2_lo, arg2_hi = split(cmd.args[1])
                        result_lo, result_hi = split(result)

                        borrow = new_name('borrow', defns)
                        cmds.append(Cmd([result_lo, borrow], 'sbc', None, [arg1_lo, arg2_lo, '1']))
                        cmds.append(Cmd([result_hi, '_'], 'sbc', None, [arg1_hi, arg2_hi, borrow]))
                elif cmd.op == 'lsr':
                    if cmd.size == 1:
                        cmds.append(Cmd(cmd.results, 'ror', None, cmd.args + ['0']))
                    else:
                        (result,) = cmd.results

                        arg_lo, arg_hi = split(cmd.args[0])
                        result_lo, result_hi = split(result)

                        carry = new_name('carry', defns)
                        cmds.append(Cmd([result_hi, carry], 'ror', None, [arg_hi, '0']))
                        cmds.append(Cmd([result_lo, '_'], 'ror', None, [arg_lo, carry]))
                elif cmd.op == 'eq':
                    assert cmd.size in (1, 2)
                    if cmd.size == 1:
                        cmd.size = None
                    else:
                        (result,) = cmd.results

                        arg1_lo, arg1_hi = split(cmd.args[0])
                        arg2_lo, arg2_hi = split(cmd.args[1])
                        eq_lo = new_name('eq_lo', defns)
                        eq_hi = new_name('eq_hi', defns)

                        cmds.append(Cmd([eq_lo, '_'], 'cmp', None, [arg1_lo, arg2_lo]))
                        cmds.append(Cmd([eq_hi, '_'], 'cmp', None, [arg1_hi, arg2_hi]))
                        cmds.append(Cmd([result], 'and', None, [eq_lo, eq_hi]))
                elif cmd.op == 'ge':
                    assert cmd.size in (1, 2)
                    if cmd.size == 1:
                        cmd.size = None
                    else:
                        (result,) = cmd.results

                        arg1_lo, arg1_hi = split(cmd.args[0])
                        arg2_lo, arg2_hi = split(cmd.args[1])
                        ge_hi = new_name('ge_hi', defns)
                        ge_lo = new_name('ge_lo', defns)
                        eq_hi = new_name('eq_hi', defns)
                        ne_hi = new_name('ne_hi', defns)
                        t = new_name('t', defns)

                        cmds.append(Cmd([eq_hi, ge_hi], 'cmp', None, [arg1_hi, arg2_hi]))
                        cmds.append(Cmd(['_', ge_lo], 'cmp', None, [arg1_lo, arg2_lo]))
                        cmds.append(Cmd([ne_hi], 'not', None, [eq_hi]))
                        cmds.append(Cmd([t], 'or', None, [ne_hi, ge_lo]))
                        cmds.append(Cmd([result], 'and', None, [ge_hi, t]))
                elif cmd.op == 'store':
                    assert cmd.size in (1, 2)
                    if cmd.size == 1:
                        addr_lo, addr_hi = split(cmd.args[0])
                        cmds.append(Cmd([], 'store', None, [addr_lo, addr_hi, cmd.args[1]]))
                    else:
                        fixed = False
                        arg_lo, arg_hi = split(cmd.args[1])
                        cmds.append(Cmd([], 'store', 1, [cmd.args[0], arg_lo]))
                        next_addr = new_name('next_addr', defns)
                        cmds.append(Cmd([next_addr], 'add', 2, [cmd.args[0], '1']))
                        cmds.append(Cmd([], 'store', 1, [next_addr, arg_hi]))
                elif cmd.op == 'split':
                    if len(cmd.results) == 1:
                        cmds.append(cmd)
                    else:
                        assert len(cmd.results) == 2, cmd
                        arg_lo, arg_hi = split(cmd.args[0])
                        if cmd.results[0] != '_':
                            cmds.append(Cmd([cmd.results[0]], 'copy', None, [arg_lo]))
                        if cmd.results[1] != '_':
                            cmds.append(Cmd([cmd.results[1]], 'copy', None, [arg_hi]))
                else:
                    assert False, cmd
            block.cmds = cmds

    fixed = False
    while not fixed:
        fixed = True
        for block in blocks:
            cmds = []
            for cmd in block.cmds:
                if (any(r in split_vars for r in cmd.results) or
                    any(a in split_vars for a in cmd.args)):
                    fixed = False

                    if cmd.op == 'phi':
                        (result,) = cmd.results
                        result_lo, result_hi = split(result)

                        args_lo = []
                        args_hi = []
                        for i, arg in enumerate(cmd.args):
                            if i % 2:
                                arg_lo, arg_hi = split(arg)
                                args_lo.append(arg_lo)
                                args_hi.append(arg_hi)
                            else:
                                args_lo.append(arg)
                                args_hi.append(arg)

                        cmds.append(Cmd([result_lo], 'phi', None, args_lo))
                        cmds.append(Cmd([result_hi], 'phi', None, args_hi))
                    elif cmd.op == 'save':
                        for arg in cmd.args:
                            arg_lo, arg_hi = split(arg)
                            cmds.append(Cmd([], 'save', None, [arg_lo]))
                            cmds.append(Cmd([], 'save', None, [arg_hi]))
                    elif cmd.op == 'restore':
                        for result in cmd.results:
                            result_lo, result_hi = split(result)
                            cmds.append(Cmd([result_hi], 'restore', None, []))
                            cmds.append(Cmd([result_lo], 'restore', None, []))
                    else:
                        assert False, cmd

                else:
                    cmds.append(cmd)
            block.cmds = cmds

    for block in blocks:
        for cmd in block.cmds:
            for result in cmd.results:
                assert result not in split_vars, cmd
            for arg in cmd.args:
                assert arg not in split_vars, cmd

    remove_copies(blocks)


def add_z_results(blocks):
    for block in blocks:
        for cmd in block.cmds:
            if cmd.op not in ('adc', 'sbc', 'ror', 'restore'):
                continue
            cmd.results.append('_')


def const_adc(blocks):
    fixed = True
    for block in blocks:
        cmds = []
        for cmd in block.cmds:
            if cmd.op == 'adc':
                try:
                    left = int(cmd.args[0], 0)
                    right = int(cmd.args[1], 0)
                    carry = int(cmd.args[2], 0)
                except ValueError:
                    cmds.append(cmd)
                    continue
                fixed = False
                s = left + right + carry
                c = 0
                if s >= 256:
                    s -= 256
                    c = 1
                if cmd.results[0] != '_':
                    cmds.append(Cmd([cmd.results[0]], 'copy', None, [str(s)]))
                if cmd.results[1] != '_':
                    cmds.append(Cmd([cmd.results[1]], 'copy', None, [str(c)]))
            else:
                cmds.append(cmd)
        block.cmds = cmds

    remove_copies(blocks)
    return fixed


def not_br(blocks):
    fixed = True
    nots = {}
    for block in blocks:
        for cmd in block.cmds:
            if cmd.op == 'not':
                (result,) = cmd.results
                (arg,) = cmd.args
                nots[result] = arg

    nots_use_count = Counter()
    for block in blocks:
        for cmd in block.cmds:
            for arg in cmd.args:
                if arg in nots:
                    nots_use_count[arg] += 1

    nots_only_used_in_br = set()
    for block in blocks:
        for cmd in block.cmds:
            if cmd.op == 'br' and nots_use_count[cmd.args[0]] == 1:
                nots_only_used_in_br.add(cmd.args[0])

    for block in blocks:
        cmds = []
        for cmd in block.cmds:
            if cmd.op == 'not':
                if cmd.results[0] not in nots_only_used_in_br:
                    cmds.append(cmd)
            elif cmd.op == 'br':
                if cmd.args[0] in nots_only_used_in_br:
                    fixed = False
                    cmds.append(Cmd([], 'br', None, [nots[cmd.args[0]], cmd.args[2], cmd.args[1]]))
                else:
                    cmds.append(cmd)
            else:
                cmds.append(cmd)
        block.cmds = cmds

    return fixed


def and_or_br(blocks):
    orig_blocks = blocks

    fixed = True
    ands = {}
    ors = {}
    for block in blocks:
        for cmd in block.cmds:
            if cmd.op == 'and' or cmd.op == 'or':
                (result,) = cmd.results
                if cmd.op == 'and':
                    ands[result] = cmd.args
                else:
                    ors[result] = cmd.args


    use_count = Counter()
    for block in blocks:
        for cmd in block.cmds:
            for arg in cmd.args:
                if arg in ands or arg in ors:
                    use_count[arg] += 1

    only_used_in_br = set()
    for block in blocks:
        for cmd in block.cmds:
            if cmd.op == 'br' and use_count[cmd.args[0]] == 1:
                only_used_in_br.add(cmd.args[0])

    block_names = set(b.name for b in blocks)
    new_blocks = []
    for block in blocks:
        cmds = []
        for cmd in block.cmds:
            if cmd.op == 'and' or cmd.op == 'or':
                if cmd.results[0] not in only_used_in_br:
                    cmds.append(cmd)
            elif cmd.op == 'br':
                if cmd.args[0] in only_used_in_br:
                    fixed = False
                    if cmd.args[0] in ands:
                        lhs, rhs = ands[cmd.args[0]]
                        new_block_name = new_name(block.name, block_names)
                        cmds.append(Cmd([], 'br', None, [lhs, new_block_name, cmd.args[2]]))
                        block.cmds = cmds
                        new_blocks.append(block)
                        block = Block(new_block_name, [])
                        cmds = []
                        cmds.append(Cmd([], 'br', None, [rhs, cmd.args[1], cmd.args[2]]))
                    else:
                        lhs, rhs = ors[cmd.args[0]]
                        new_block_name = new_name(block.name, block_names)
                        cmds.append(Cmd([], 'br', None, [lhs, cmd.args[1], new_block_name]))
                        block.cmds = cmds
                        new_blocks.append(block)
                        block = Block(new_block_name, [])
                        cmds = []
                        cmds.append(Cmd([], 'br', None, [rhs, cmd.args[1], cmd.args[2]]))
                else:
                    cmds.append(cmd)
            else:
                cmds.append(cmd)
        block.cmds = cmds
        new_blocks.append(block)
        blocks = new_blocks

    orig_blocks.clear()
    orig_blocks.extend(blocks)
    return fixed


def push_down_unique_uses(blocks):
    use_counts = Counter()
    used_in_phi = set()
    for block in blocks:
        for cmd in block.cmds:
            for arg in cmd.args:
                if cmd.op == 'phi':
                    used_in_phi.add(arg)
                use_counts[arg] += 1

    unique = {}

    for block in blocks:
        cmds = []
        for cmd in block.cmds:
            if cmd.op in ('phi', 'restore'):
                cmds.append(cmd)
                continue

            def uniquely_used_result():
                result = None
                for r in cmd.results:
                    if r == '_':
                        continue
                    if r in used_in_phi:
                        return None
                    if use_counts[r] != 1:
                        return None
                    if result is not None:
                        return None
                    result = r
                return result

            result = uniquely_used_result()
            if result is None:
                cmds.append(cmd)
                continue
            unique[result] = cmd
        block.cmds = cmds

    while unique:
        for block in blocks:
            cmds = []
            for cmd in block.cmds:
                for arg in reversed(cmd.args):
                    if arg in unique:
                        cmds.append(unique[arg])
                        del unique[arg]
                cmds.append(cmd)
            block.cmds = cmds


def cse(blocks):
    fixed = True
    doms = dominators(blocks)

    blocks_by_name = {}
    for block in blocks:
        blocks_by_name[block.name] = block

    for block in blocks:
        cmds = []
        for cmd in block.cmds:
            if cmd.op in ('br', 'jsr', 'rts', 'save', 'restore', 'store'):
                cmds.append(cmd)
                continue

            def find_dom_cmd():
                for dom_cmd in block.cmds:
                    if dom_cmd is cmd:
                        break
                    if cmd.op == dom_cmd.op and cmd.args == dom_cmd.args:
                        return dom_cmd

                for dom in doms[block.name]:
                    if dom == block.name:
                        continue
                    dom = blocks_by_name[dom]
                    for dom_cmd in dom.cmds:
                        if cmd.op == dom_cmd.op and cmd.args == dom_cmd.args:
                            return dom_cmd

            dom_cmd = find_dom_cmd()
            if dom_cmd is None:
                cmds.append(cmd)
                continue
            fixed = False
            for i in range(len(cmd.results)):
                if cmd.results[i] == '_':
                    continue
                if dom_cmd.results[i] == '_':
                    dom_cmd.results[i] = cmd.results[i]
                else:
                    cmds.append(Cmd([cmd.results[i]], 'copy', None, [dom_cmd.results[i]]))
        block.cmds = cmds

    remove_copies(blocks)
    return fixed


def get_blocks_definitions(blocks):
    defns = set()
    for block in blocks:
        for cmd in block.cmds:
            defns |= set(cmd.results)
    return defns


def new_name(name, defns):
    if name == '_':
        return name
    candidates = itertools.chain([name], (f'{name}{n}' for n in itertools.count(1)))
    chosen = next(c for c in candidates if c not in defns)
    defns.add(chosen)
    return chosen


def dominators(blocks):
    preds = collect_predecessors(blocks)

    jsr_dom = {}
    for block in blocks:
        for cmd in block.cmds:
            if cmd.op == 'jsr':
                jsr_dom[cmd.args[1]] = block.name


    doms = defaultdict(set)
    for block in blocks:
        if not preds[block.name]:
            doms[block.name] = {block.name}
            continue
        for block2 in blocks:
            if block2.name != block.name:
                doms[block.name].add(block2.name)

    fixed = False
    while not fixed:
        fixed = True
        for block in blocks:
            if not preds[block.name]:
                continue
            new_doms = {block.name} | set.intersection(*(doms[p.name] for p in preds[block.name]))
            if block.name in jsr_dom:
                new_doms |= doms[jsr_dom[block.name]]
            if new_doms != doms[block.name]:
                fixed = False
            doms[block.name] = new_doms

    return doms


def ge_zero(blocks):
    fixed = True
    for block in blocks:
        cmds = []
        for cmd in block.cmds:
            if cmd.op == 'cmp' and cmd.args[1] == '0' and cmd.results[1] != '_':
                fixed = False
                if cmd.results[0] != '_':
                    cmds.append(Cmd([cmd.results[0], '_'], 'cmp', None, cmd.args))
                cmds.append(Cmd([cmd.results[1]], 'copy', None, ['true']))
            else:
                cmds.append(cmd)
        block.cmds = cmds

    remove_copies(blocks)
    return fixed


def const_and(blocks):
    fixed = True
    for block in blocks:
        cmds = []
        for cmd in block.cmds:
            if cmd.op == 'and' and any(a in ('true', 'false') for a in cmd.args):
                fixed = False
                if all(a in ('true', 'false') for a in cmd.args):
                    result = 'true' if cmd.args[0] == 'true' and cmd.args[1] == 'true' else 'false'
                    cmds.append(Cmd(cmd.results, 'copy', None, [result]))
                else:
                    if cmd.args[0] not in ('true', 'false'):
                        cmd.args[0], cmd.args[1] = cmd.args[1], cmd.args[0]
                    if cmd.args[0] == 'true':
                        cmds.append(Cmd(cmd.results, 'copy', None, [cmd.args[1]]))
                    else:
                        cmds.append(Cmd(cmd.results, 'copy', None, ['false']))
            else:
                cmds.append(cmd)
        block.cmds = cmds

    remove_copies(blocks)
    return fixed


def redundant_cmp_zero(blocks):
    fixed = True

    defns = {}
    for block in blocks:
        for cmd in block.cmds:
            for result in cmd.results:
                if result != '_':
                    defns[result] = cmd

    defns_set = get_blocks_definitions(blocks)

    phis_for_block = defaultdict(list)
    cmps_for_block = defaultdict(list)

    for block in blocks:
        cmds = []
        for cmd in block.cmds:
            if cmd.op == 'cmp' and cmd.args[1] == '0':
                assert cmd.results[1] == '_'
                if cmd.args[0] not in defns:
                    v = int(cmd.args[0])
                    cmds.append(Cmd([cmd.results[0]], 'copy', None, ['1' if v else '0']))
                    continue
                defn = defns[cmd.args[0]]
                if defn.op == 'phi':
                    fixed = False
                    phi_args = []
                    for i in range(0, len(defn.args), 2):
                        pred = defn.args[i]
                        arg = defn.args[i+1]
                        cmp_name = new_name(f'{arg}_eq', defns_set)
                        cmp = Cmd([cmp_name, '_'], 'cmp', None, [arg, '0'])
                        cmps_for_block[pred].append(cmp)
                        phi_args.append(pred)
                        phi_args.append(cmp_name)

                    phi_name = new_name(f'{defn.results[0]}_eq', defns_set)
                    phis_for_block[block.name].append(Cmd([phi_name], 'phi', None, phi_args))
                    source = phi_name
                else:
                    if defn.results[-1] == '_':
                        defn.results[-1] = new_name('eq', defns_set)
                    source = defn.results[-1]
                cmds.append(Cmd([cmd.results[0]], 'copy', None, [source]))
            else:
                cmds.append(cmd)
        block.cmds = cmds

    for block in blocks:
        block.cmds = [*phis_for_block[block.name], *block.cmds[:-1], *cmps_for_block[block.name], block.cmds[-1]]

    return fixed



def from_ssa(blocks):
    new_blocks = []

    block_names = set(b.name for b in blocks)
    phi_headers = {}

    for block in blocks:
        copies_for_predecessor = {}

        cmds = []
        for cmd in block.cmds:
            if cmd.op != 'phi':
                cmds.append(cmd)
                continue
            for i in range(0, len(cmd.args), 2):
                pred = cmd.args[i]
                arg = cmd.args[i+1]
                if pred not in copies_for_predecessor:
                    copies_for_predecessor[pred] = []
                copies_for_predecessor[pred].append(Cmd(cmd.results, 'copy', None, [arg]))
        block.cmds = cmds

        for pred, copies in copies_for_predecessor.items():
            name = new_name(f'{block.name}_from_{pred}', block_names)
            br = Cmd([], 'br', None, [block.name])
            header = Block(name, [*copies, br])
            phi_headers[pred, block.name] = header
            new_blocks.append(header)
        new_blocks.append(block)

    for block in blocks:
        term = block.cmds[-1]
        if term.op == 'rts':
            continue
        if term.op == 'br':
            if len(term.args) == 1:
                if (block.name, term.args[0]) in phi_headers:
                    term.args[0] = phi_headers[block.name, term.args[0]].name
            else:
                if (block.name, term.args[1]) in phi_headers:
                    term.args[1] = phi_headers[block.name, term.args[1]].name
                if (block.name, term.args[2]) in phi_headers:
                    term.args[2] = phi_headers[block.name, term.args[2]].name
        else:
            assert term.op == 'jsr'
            if (block.name, term.args[0]) in phi_headers:
                header = phi_headers[block.name, term.args[0]]
                block.cmds[-1] = Cmd([], 'br', None, [header.name])
                header.cmds[-1] = term

    blocks.clear()
    blocks.extend(new_blocks)


def compute_blocks_live_sets(blocks):
    live_ins = {}
    live_outs = {}

    defns = get_blocks_definitions(blocks)
    blocks_by_name = {}

    for block in blocks:
        blocks_by_name[block.name] = block
        live_ins[block.name] = set()
        live_outs[block.name] = set()

    fixed = False
    while not fixed:
        fixed = True

        for block in blocks:
            def successors():
                term = block.cmds[-1]
                if term.op == 'br':
                    if len(term.args) == 1:
                        return term.args
                    else:
                        return term.args[1:]
                else:
                    # TODO: JSR, RTS
                    return []

            for succ in successors():
                if not (live_ins[succ] <= live_outs[block.name]):
                    fixed = False
                    live_outs[block.name] |= live_ins[succ]

                for cmd in blocks_by_name[succ].cmds:
                    if cmd.op != 'phi':
                        break
                    for i in range(0, len(cmd.args), 2):
                        b = cmd.args[i]
                        arg = cmd.args[i+1]
                        if b == block.name and arg in defns and arg not in live_outs[block.name]:
                            fixed = False
                            live_outs[block.name].add(arg)

            live = copy.deepcopy(live_outs[block.name])
            for cmd in reversed(block.cmds):
                live -= set(cmd.results)
                if cmd.op != 'phi':
                    live |= set(cmd.args) & defns
            if live != live_ins[block.name]:
                fixed = False
                live_ins[block.name] = live

    return live_ins, live_outs


funcs = parse()

for func in funcs:
    to_ssa(func.blocks)
    compute_live_sets(func)

break_live_ranges_across_recursive_calls(funcs)

blocks = merge_all_funcs(funcs)

to_ssa(blocks)
lower_cmp(blocks)
lower_16(blocks)
add_z_results(blocks)

fixed = False
while not fixed:
    fixed = True
    fixed &= const_adc(blocks)
    fixed &= ge_zero(blocks)
    fixed &= const_and(blocks)

fixed = False
while not fixed:
    fixed = True
    fixed &= redundant_cmp_zero(blocks)
remove_copies(blocks)

fixed = False
while not fixed:
    fixed = True
    fixed &= cse(blocks)

fixed = False
while not fixed:
    fixed = True
    fixed &= not_br(blocks)
    fixed &= and_or_br(blocks)

push_down_unique_uses(blocks)

live_ins, live_outs = compute_blocks_live_sets(blocks)

for block in blocks:
    print(live_ins[block.name])
    print(block)
    print(live_outs[block.name])
    print()

# from_ssa(blocks)

# for block in blocks:
#     print(block)
