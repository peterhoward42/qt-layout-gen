from unittest import TestCase

from qtlayoutbuilder.lib import string_utils
from qtlayoutbuilder.lib.string_utils import MultilineString


class StringUtilsTest(TestCase):
    # First 'plain' string functions.

    def test_get_leading_spaces(self):
        # Normal usage.
        string, length = string_utils.get_leading_spaces('   foo')
        self.assertEquals(string, '   ')
        self.assertEquals(length, 3)

        # When there are no leading spaces.
        string, length = string_utils.get_leading_spaces('foo')
        self.assertEquals(string, '')
        self.assertEquals(length, 0)

        # On empty string
        string, length = string_utils.get_leading_spaces('')
        self.assertEquals(string, '')
        self.assertEquals(length, 0)

    # Now multiline string functions.

    def test_remove_empty_first_line(self):
        # Normal usage
        result = MultilineString.remove_empty_first_line("""
        foo
        bar
        """)
        self.assertTrue(result.startswith('        foo'))

        # When first line is not empty.
        result = MultilineString.remove_empty_first_line("""x
        foo
        bar
        """)
        self.assertTrue(result.startswith('x\n'))

    def test_shift_left(self):
        # Normal usage
        input = """
            foo
              bar
                baz
        """
        input = MultilineString.remove_empty_first_line(input)
        result = MultilineString.shift_left(input)
        lines = result.split('\n')
        self.assertEqual(lines[0], 'foo')
        self.assertEqual(lines[1], '  bar')
        self.assertEqual(lines[2], '    baz')
