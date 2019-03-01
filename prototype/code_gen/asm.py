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
"""Classes representing 6502 assembly language instructions.

Some things to note about this architecture:
    - In every instruction where the Z or N register is set, there is some operative
      value that is used to do so. Z is set to whether this value is zero, and N is set
      two whether that value is negative if interpreted in base 2.
"""

import attr


@attr.s
class TAX:
    """Transfers the A register to the X register.

    Sets N and Z based on the value in A.
    """


@attr.s
class TAY:
    """Transfers the A register to the Y register.

    Sets N and Z based on the value in A.
    """


@attr.s
class TXA:
    """Transfers the X register to the A register.

    Sets N and Z based on the value in X.
    """


@attr.s
class TYA:
    """Transfers the Y register to the A register.

    Sets N and Z based on the value in Y.
    """


@attr.s
class STA:
    """Stores the A register to a memory address."""
    address = attr.ib()


@attr.s
class LDA:
    """Loads the contents of a memory address to the A register.

    Sets N and Z based on the contents of the memory address.
    """
    address = attr.ib()


@attr.s
class PHP:
    """Pushes all status registers onto the stack as a single byte.

    The pushed byte is mapped to flags as follows:
    Bit number: 7 6 5 4 3 2 1 0
    Flag:       N V - - D I Z C
    """


@attr.s
class PLP:
    """Pulls all status registers off of the stack.

    The popped byte is interpreted as in PHP.
    """
