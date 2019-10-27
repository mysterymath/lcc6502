import unittest
from textwrap import dedent

from parse import parse_lines

class TestToSsa(unittest.TestCase):
  def test_basic_parse(self):
    (func,) = parse_lines("""
      main
        start
          ret
      end
    """)
    self.assertMultiLineEqual(str(func), dedent("""\
      main
        start
          ret
      end
    """))