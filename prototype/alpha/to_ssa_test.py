from to_ssa import to_ssa

import unittest
from textwrap import dedent

from parse import parse_lines


class TestToSsa(unittest.TestCase):
  def test_renumbers_defns(self):
    (func,) = parse_lines("""
      main
        start
          a = add 1 1
          b = add 2 2
          a = add 3 3
          ret
      end
    """)
    to_ssa(func.blocks)
    self.assertMultiLineEqual(str(func), dedent("""\
      main
        start
          a = add 1 1
          b = add 2 2
          a1 = add 3 3
          ret
      end
    """))

  def test_renumbers_uses_in_same_block(self):
    (func,) = parse_lines("""
      main
        start
          a = add 1 1
          a = add 2 2
          b = add 3 3
          b = add a b
          ret
      end
    """)
    to_ssa(func.blocks)
    self.assertMultiLineEqual(str(func), dedent("""\
      main
        start
          a = add 1 1
          a1 = add 2 2
          b = add 3 3
          b1 = add a1 b
          ret
      end
    """))

  def test_renumbers_uses_across_br(self):
    (func,) = parse_lines("""
      main
        start
          a = add 1 1
          a = add 2 2
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
          a = add 1 1
          a1 = add 2 2
          br next
        next
          b = add a1 1
          ret
      end
    """))

  def test_inserts_phi(self):
    (func,) = parse_lines("""
      main
        start
          br 1 left right
        left
          a = add 1 1
          a = add 2 2
          br join
        right
          a = add 3 3
          a = add 4 4
          br join
        join
          b = add a a
          ret
      end
    """)
    to_ssa(func.blocks)
    self.assertMultiLineEqual(str(func), dedent("""\
      main
        start
          br 1 left right
        left
          a = add 1 1
          a1 = add 2 2
          br join
        right
          a2 = add 3 3
          a3 = add 4 4
          br join
        join
          a4 = phi left a1 right a3
          b = add a4 a4
          ret
      end
    """))

  def test_renumbers_phi_args(self):
    (func,) = parse_lines("""
      main
        start
          br 1 left right
        left
          a = add 1 1
          a = add 2 2
          br join
        right
          b = add 3 3
          b = add 4 4
          br join
        join
          c = phi left a right b
          ret
      end
    """)
    to_ssa(func.blocks)
    self.assertMultiLineEqual(str(func), dedent("""\
      main
        start
          br 1 left right
        left
          a = add 1 1
          a1 = add 2 2
          br join
        right
          b = add 3 3
          b1 = add 4 4
          br join
        join
          c = phi left a1 right b1
          ret
      end
    """))

  def test_renumbers_uses_across_rts(self):
    (func,) = parse_lines("""
      main
        start
          jsr foo footer
        foo
          a = add 1 1
          a = add 2 2
          rts footer
        footer
          b = add a a
          ret
      end
    """)
    to_ssa(func.blocks)
    self.assertMultiLineEqual(str(func), dedent("""\
      main
        start
          jsr foo footer
        foo
          a = add 1 1
          a1 = add 2 2
          rts footer
        footer
          b = add a1 a1
          ret
      end
    """))

  def test_renumbers_uses_across_subroutine_call(self):
    (func,) = parse_lines("""
      main
        start
          a = add 1 1
          a = add 2 2
          jsr foo footer
        foo
          rts footer
        footer
          b = add a a
          ret
      end
    """)
    to_ssa(func.blocks)
    self.assertMultiLineEqual(str(func), dedent("""\
      main
        start
          a = add 1 1
          a1 = add 2 2
          jsr foo footer
        foo
          rts footer
        footer
          b = add a1 a1
          ret
      end
    """))
