from unittest import TestCase

from qtlayoutbuilder.lib import regex_helpers

class TestRegexHelpers(TestCase):

    def test_with_hash_style_comment_removed(self):

        original = 'foobar'
        removed = regex_helpers.with_hash_style_comment_removed(original)
        self.assertEquals(removed, 'foobar')

        original = 'foo#bar'
        removed = regex_helpers.with_hash_style_comment_removed(original)
        self.assertEquals(removed, 'foo')

        original = 'foo#bar#baz'
        removed = regex_helpers.with_hash_style_comment_removed(original)
        self.assertEquals(removed, 'foo')

        original = '#foo'
        removed = regex_helpers.with_hash_style_comment_removed(original)
        self.assertEquals(removed, '')

    def test_with_parenthesis_removed(self):
        input = 'foo(bar)baz'
        output = regex_helpers.with_parenthesis_removed(input)
        self.assertEquals(output, 'foobaz')
