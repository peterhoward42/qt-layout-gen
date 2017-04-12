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

    def test_isolate_parenthesised_bit(self):
        # Canonical case.
        original = 'foo(bar)baz'
        paren, remainder = regex_helpers.isolate_parenthesised_bit(original)
        self.assertEquals(paren, 'bar')
        self.assertEquals(remainder, 'foobaz')

        # Behaves when non paren present.
        original = 'foobar'
        paren, remainder = regex_helpers.isolate_parenthesised_bit(original)
        self.assertEquals(paren, '')
        self.assertEquals(remainder, 'foobar')

        # Behaves when paren is everything.
        original = '(foo)'
        paren, remainder = regex_helpers.isolate_parenthesised_bit(original)
        self.assertEquals(paren, 'foo')
        self.assertEquals(remainder, '')

        # Regex is greedy.
        original = 'foo(bar)baz(billy)'
        paren, remainder = regex_helpers.isolate_parenthesised_bit(original)
        self.assertEquals(paren, 'bar)baz(billy')
        self.assertEquals(remainder, 'foo')
