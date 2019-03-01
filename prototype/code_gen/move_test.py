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
"""Unit tests for the Move instruction."""

import pytest

import asm
import move
from var import Variable


def test_null():
    """Test that a null move can be emitted."""
    source = Variable("from")
    destination = Variable("to")
    allocation = {source: set(), destination: set()}

    assert move.Move(destination, source).generate(allocation, set()) == []


def test_a_to_x():
    """Test that a TAX instruction can be emitted."""
    source = Variable("from")
    destination = Variable("to")
    allocation = {source: {"A"}, destination: {"X"}}

    assert move.Move(destination, source).generate(allocation,
                                                   set()) == [asm.TAX()]


def test_a_to_y():
    """Test that a TAY instruction can be emitted."""
    source = Variable("from")
    destination = Variable("to")
    allocation = {source: {"A"}, destination: {"Y"}}

    assert move.Move(destination, source).generate(allocation,
                                                   set()) == [asm.TAY()]


def test_y_to_a():
    """Test that a TYA instruction can be emitted."""
    source = Variable("from")
    destination = Variable("to")
    allocation = {source: {"Y"}, destination: {"A"}}

    assert move.Move(destination, source).generate(allocation,
                                                   set()) == [asm.TYA()]


def test_x_to_a():
    """Test that a TXA instruction can be emitted."""
    source = Variable("from")
    destination = Variable("to")
    allocation = {source: {"X"}, destination: {"A"}}

    assert move.Move(destination, source).generate(allocation,
                                                   set()) == [asm.TXA()]


def test_x_to_y():
    """Test that X can be moved to Y through A."""
    source = Variable("from")
    destination = Variable("to")
    allocation = {source: {"X"}, destination: {"Y"}}

    assert move.Move(destination, source).generate(
        allocation, set()) == [asm.TXA(), asm.TAY()]


def test_x_to_y_a_live():
    """Test that X can be moved to Y through A when A is live by saving A."""
    source = Variable("from")
    destination = Variable("to")
    live = Variable("live")
    allocation = {source: {"X"}, destination: {"Y"}, live: {"A"}}

    assert move.Move(destination, source).generate(
        allocation, {live}) == [asm.STA(0),
                                asm.TXA(),
                                asm.TAY(),
                                asm.LDA(0)]


def test_a_to_xz():
    """Test that a TAX instruction is considered to set to both X and Z."""
    source = Variable("from")
    destination = Variable("to")
    allocation = {source: {"A"}, destination: {"X", "Z"}}

    assert move.Move(destination, source).generate(allocation,
                                                   set()) == [asm.TAX()]


def test_a_to_yz():
    """Test that a TAY instruction is considered to set to both Y and Z."""
    source = Variable("from")
    destination = Variable("to")
    allocation = {source: {"A"}, destination: {"Y", "Z"}}

    assert move.Move(destination, source).generate(allocation,
                                                   set()) == [asm.TAY()]


def test_from_nothing_fails():
    """Test that a move from nowhere cannot be emitted."""
    source = Variable("from")
    destination = Variable("to")
    allocation = {source: set(), destination: {"X"}}

    with pytest.raises(move.GenerationError):
        move.Move(destination, source).generate(allocation, set())


def test_tax_y_live():
    """Test that a TAX move with Y live can be emitted."""
    source = Variable("from")
    destination = Variable("to")
    live = Variable("live")
    allocation = {source: {"A"}, destination: {"X"}, live: {"Y"}}

    assert move.Move(destination, source).generate(allocation,
                                                   {live}) == [asm.TAX()]


def test_tax_n_live():
    """Test that a TAX move with N live can be emitted."""
    source = Variable("from")
    destination = Variable("to")
    live = Variable("live")
    allocation = {source: {"A"}, destination: {"X"}, live: {"N"}}

    assert move.Move(destination, source).generate(
        allocation, {live}) == [asm.PHP(), asm.TAX(),
                                asm.PLP()]


def test_tax_z_live():
    """Test that a TAX move with Z live can be emitted."""
    source = Variable("from")
    destination = Variable("to")
    live = Variable("live")
    allocation = {source: {"A"}, destination: {"X"}, live: {"Z"}}

    assert move.Move(destination, source).generate(
        allocation, {live}) == [asm.PHP(), asm.TAX(),
                                asm.PLP()]
