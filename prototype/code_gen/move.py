# Copyright 2018 Daniel Thornburgh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Move instruction, which moves a value from one variable to another."""

from itertools import chain
from numbers import Number

import attr
from sortedcontainers import SortedDict

import asm
from var import Constant, Variable


class GenerationError(Exception):
    """Error indicating that assembly for an operation could not be generated."""


class RuleNotApplicableError(Exception):
    """Error indicating that a rule for an operation does not apply."""


@attr.attrs
class Move:
    """Sets a destination variable to have the same value as a source variable.

    The source and destination must be the same size.
    The destination cannot be constant; for this use LoadImmediate.
    """
    destination = attr.attrib(validator=attr.validators.instance_of(Variable))
    source = attr.attrib(validator=attr.validators.instance_of(Variable))

    @destination.validator
    def _check_destination_not_constant(self, _, value):
        if isinstance(value, Constant):
            raise ValueError(
                "Destination of Move cannot be constant; did you mean LoadImmediate?"
            )

    def generate(self, allocation, live_variables):
        """Returns generated assembly for the operation.

        A variable being live means that this operation must preserve its value.

        Arguments:
            allocation: The assignment of variables to storage locations.
            live_variables: The set of variables whose values must be preserved.
        """
        if isinstance(self.source, Constant):
            # Create a temporary constant variable with self.source's value.
            # Update the allocation so that the new temp location is assigned to the same locs
            #     as self.source.
            # LoadImmediate the temporary with the new allocation.
            raise GenerationError("Constant sources not yet implemented.")
        else:
            start = {}
            for loc in allocation[self.source]:
                start[loc] = self.source
            for var in live_variables:
                for loc in allocation[var]:
                    start[loc] = var

            closed = set()
            open_ = SortedDict({0: [(start, [])]})
            while open_:
                cost, list_ = open_.peekitem(0)
                if not list_:
                    del open_[cost]
                    continue
                state, state_asm = list_.pop()

                if frozenset(state.items()) in closed:
                    continue

                if self._is_goal(state, allocation, live_variables):
                    return state_asm

                closed.add(frozenset(state.items()))

                for new_state, move_asm in chain(
                        _tax(state), _tay(state), _txa(state), _tya(state),
                        _sta_zp(state), _sta_m(state), _lda(state),
                        _php(state), _plp(state)):
                    open_.setdefault(cost + 2, []).append(
                        (new_state, state_asm + move_asm))
            raise GenerationError("Goal could not be reached.")

    def _is_goal(self, state, allocation, live_variables):
        for loc in allocation[self.destination]:
            # NOTE: Each destination location is set to the source value.
            if loc not in state or state[loc] != self.source:
                return False
        for var in live_variables:
            for loc in allocation[var]:
                if loc not in state or state[loc] != var:
                    return False
        return True

    # TODO: Only support flag locations for boolean variables

    # TODO: Provide library support for cleanly defining moves.

    # TODO: Test the moves and the overall search in isolation, since they are
    # reasonably general-purpose.

    # TODO: Configurable memory locations.


def _tax(state):
    if "A" not in state:
        return
    if "X" in state and state["X"] == state["A"]:
        return
    new_state = state.copy()
    new_state["X"] = state["A"]
    try:
        del new_state["N"]
    except KeyError:
        pass
    new_state["Z"] = state["A"]
    yield new_state, [asm.TAX()]


def _tay(state):
    if "A" not in state:
        return
    if "Y" in state and state["Y"] == state["A"]:
        return
    new_state = state.copy()
    new_state["Y"] = state["A"]
    try:
        del new_state["N"]
    except KeyError:
        pass
    new_state["Z"] = state["A"]
    yield new_state, [asm.TAY()]


def _txa(state):
    if "X" not in state:
        return
    if "A" in state and state["A"] == state["X"]:
        return
    new_state = state.copy()
    new_state["A"] = state["X"]
    try:
        del new_state["N"]
    except KeyError:
        pass
    new_state["Z"] = state["X"]
    yield new_state, [asm.TXA()]


def _tya(state):
    if "Y" not in state:
        return
    if "A" in state and state["A"] == state["Y"]:
        return
    new_state = state.copy()
    new_state["A"] = state["Y"]
    try:
        del new_state["N"]
    except KeyError:
        pass
    new_state["Z"] = state["Y"]
    yield new_state, [asm.TYA()]


def _sta_zp(state):
    if "A" not in state:
        return
    for loc in state:
        if isinstance(loc, Number) and loc < 256 and state[loc] == state["A"]:
            return

    for loc in range(256):
        if loc in state:
            continue

        new_state = state.copy()
        new_state[loc] = state["A"]
        yield new_state, [asm.STA(loc)]
        return


def _sta_m(state):
    if "A" not in state:
        return
    for loc in state:
        if isinstance(loc, Number) and loc >= 256 and state[loc] == state["A"]:
            return

    for loc in range(256, 65536):
        if loc in state:
            continue

        new_state = state.copy()
        new_state[loc] = state["A"]
        yield new_state, [asm.STA(loc)]
        return


def _lda(state):
    for loc in state:
        if isinstance(loc, Number) and loc < 256 and state[loc] != state["A"]:
            new_state = state.copy()
            new_state["A"] = state[loc]
            try:
                del new_state["N"]
            except KeyError:
                pass
            new_state["Z"] = state[loc]
            yield new_state, [asm.LDA(loc)]


def _php(state):
    flags = {}
    for loc in ("N", "Z"):
        if loc in state:
            flags[loc] = state[loc]
    if not flags:
        return
    flags = frozenset(flags.items())
    new_state = state.copy()
    if "stack" not in new_state:
        new_state["stack"] = (flags, )
    else:
        if flags in new_state["stack"]:
            return
        new_state["stack"] += (flags, )
    yield new_state, [asm.PHP()]


def _plp(state):
    if "stack" not in state:
        return
    flags = dict(state["stack"][-1])
    new_state = state.copy()
    for loc in ("N", "Z"):
        try:
            del new_state[loc]
        except KeyError:
            pass
    for loc in flags:
        new_state[loc] = flags[loc]
    new_state["stack"] = new_state["stack"][:-1]
    if not new_state["stack"]:
        del new_state["stack"]
    yield new_state, [asm.PLP()]
