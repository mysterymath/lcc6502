from to_ssa import to_ssa

import unittest
from textwrap import dedent

from parse import parse_lines


class TestToSsa(unittest.TestCase):
  def test_renumbers_defns(self):
    (func,) = parse_lines("""
      main
        start
          a = add 1 2
          b = add 3 4
          a = add 5 6
          ret
      end
    """)
    to_ssa(func.blocks)
    self.assertMultiLineEqual(str(func), dedent("""\
      main
        start
          a = add 1 2
          b = add 3 4
          a1 = add 5 6
          ret
      end
    """))

  def test_renumbers_uses_in_same_block(self):
    (func,) = parse_lines("""
      main
        start
          a = add 1 2
          a = add 3 4
          b = add 5 6
          b = add a b
          ret
      end
    """)
    to_ssa(func.blocks)
    self.assertMultiLineEqual(str(func), dedent("""\
      main
        start
          a = add 1 2
          a1 = add 3 4
          b = add 5 6
          b1 = add a1 b
          ret
      end
    """))

  def test_renumbers_uses_across_br(self):
    (func,) = parse_lines("""
      main
        start
          a = add 1 2
          a = add 3 4
          br next
        next
          b = add a 1
          ret
      end
    """)
    to_ssa(func.blocks)
    self.assertMultiLineEqual(str(func), dedent("""\
      main
        start
          a = add 1 2
          a1 = add 3 4
          br next
        next
          b = add a1 1
          ret
      end
    """))