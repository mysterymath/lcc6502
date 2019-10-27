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