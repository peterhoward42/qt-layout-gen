from unittest import TestCase

from qtlayoutbuilder.lib.multiline_string_utils import MultilineString


class MultilineStringUtilsTest(TestCase):

    def test_remove_empty_first_and_last_lines(self):
        # Normal usage
        result = MultilineString.remove_empty_first_and_last_lines("""
        foo
        bar
        """)
        self.assertTrue(result.startswith('        foo'))
        self.assertTrue(result.endswith('bar'))

        # When neither first or last line is empty.
        result = MultilineString.remove_empty_first_and_last_lines("""x
        foo
        bar
        x""")
        self.assertTrue(result.startswith('x\n'))
        self.assertTrue(result.endswith('x'))

        # When input is empty.
        result = MultilineString.remove_empty_first_and_last_lines('')
        self.assertEqual(result, '')

        # When several lines exist at the beginning and / or end that are
        # whitespace only.
        result = MultilineString.remove_empty_first_and_last_lines("""
            
            foo
            bar
            
        """)
        self.assertEqual(result, '            foo\n            bar')

    def test_shift_left(self):
        # Normal usage
        str_input = """
            foo
              bar
                baz
        """
        result = MultilineString.shift_left(str_input)
        lines = result.split('\n')
        self.assertEqual(lines[0], 'foo')
        self.assertEqual(lines[1], '  bar')
        self.assertEqual(lines[2], '    baz')

    def test_normalise(self):
        str_input = """
            foo
              bar
                baz
        """
        result = MultilineString.normalise(str_input)
        lines = result.split('\n')
        self.assertEqual(lines[0], 'foo')
        self.assertEqual(lines[1], 'bar')
        self.assertEqual(lines[2], 'baz')
