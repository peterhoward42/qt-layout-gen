from unittest import TestCase

from qtlayoutbuilder.lib import regex_helpers


class TestRegexHelpers(TestCase):

    def test_with_hash_style_comment_removed(self):

        original = 'foobar'
        removed = regex_helpers.remove_comment(original)
        self.assertEquals(removed, 'foobar')

        original = 'foo#bar'
        removed = regex_helpers.remove_comment(original)
        self.assertEquals(removed, 'foo')

        original = 'foo#bar#baz'
        removed = regex_helpers.remove_comment(original)
        self.assertEquals(removed, 'foo')

        original = '#foo'
        removed = regex_helpers.remove_comment(original)
        self.assertEquals(removed, '')

    def test_with_parenthesis_removed(self):
        str_input = 'foo(bar)baz'
        output = regex_helpers.remove_parenthesis(str_input)
        self.assertEquals(output, 'foobaz')

        str_input = 'foobarbaz'
        output = regex_helpers.remove_parenthesis(str_input)
        self.assertEquals(output, 'foobarbaz')

    def test_capture_parenthesis(self):
        str_input = 'foo(bar)baz'
        output = regex_helpers.capture_parenthesis(str_input)
        self.assertEquals(output, 'bar')

        str_input = 'foo()baz'
        output = regex_helpers.capture_parenthesis(str_input)
        self.assertIsNone(output)

        str_input = 'foobarbaz'
        output = regex_helpers.capture_parenthesis(str_input)
        self.assertIsNone(output)
