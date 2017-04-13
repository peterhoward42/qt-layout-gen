from unittest import TestCase

from qtlayoutbuilder.lib import string_utils


class StringUtilsTest(TestCase):

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

    def test_measure_indent(self):
        self.assertEquals(string_utils.measure_indent('   foo'), 3)

    def test_as_list_of_words(self):
        words = string_utils.as_list_of_words('  foo  bar  ')
        self.assertEqual(words, ['foo', 'bar'])
