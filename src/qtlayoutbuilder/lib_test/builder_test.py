from unittest import TestCase

from PySide.QtGui import QHBoxLayout

from qtlayoutbuilder.api import LayoutError
from qtlayoutbuilder.lib.builder import Builder
from qtlayoutbuilder.lib_test import test_utils


class TestBuilder(TestCase):

    # Test utilities and helpers, bottom up.

    #-------------------------------------------------------------------------
    # Assertions and error reporting.

    def test_assert_multiple_of_two(self):
        self.assertIsNone(Builder._assert_multiple_of_two(4, 'mock line'))
        self.assertRaises(
                LayoutError, Builder._assert_multiple_of_two, 3, 'mock line')
        try:
            Builder._assert_multiple_of_two(3, 'mock_line')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                Indentation spaces must be a multiple of 2.
                This line: <mock_line> is indented by 3 spaces.
            """, msg))

    def test_assert_no_tabs_present(self):
        self.assertIsNone(Builder._assert_no_tabs_present('no tabs here'))
        self.assertRaises(
                LayoutError, Builder._assert_no_tabs_present, '\t')
        try:
            Builder._assert_no_tabs_present('\t')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                This line: <\t> contains a tab character -
                which is not allowed.
            """, msg))

    #-------------------------------------------------------------------------
    # Minor functions

    def test_measure_indent(self):
        self.assertEquals(Builder._measure_indent('    foo'), 4)
        self.assertRaises(LayoutError, Builder._measure_indent, '   foo')

    def test_isolate_two_words(self):
        # Properly formed.
        a,b = Builder._isolate_two_words('   foo   bar   ')
        self.assertEquals(a, 'foo')
        self.assertEquals(b, 'bar')

        # Improperly formed.
        self.assertRaises(LayoutError, Builder._isolate_two_words, 'foo bar baz')
        try:
            Builder._isolate_two_words('foo bar baz')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                Cannot isolate two words from this line: <foo bar baz>,
                after removing comments and parenthesised parts if present.
            """, msg))

    #-------------------------------------------------------------------------
    # API Level - wraps error with context properly.

    def test_context_added_to_error_messages(self):
        illegal_second_line = ('# a comment', '\t')
        self.assertRaises(
                LayoutError, Builder.build, illegal_second_line, 'unit test')
        try:
            Builder.build(illegal_second_line, 'unit test')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                This line: <	> contains a tab character -
                which is not allowed.
                (Line number 2 of unit test)
            """, msg))

    #-------------------------------------------------------------------------
    # Trivial single child addition works.

    def test_simplest_possible_child_addition(self):
        lines = (('page widget'),('  layout hbox'))
        layouts = Builder.build(lines, 'unit test')
        target = layouts.page.layout
        self.assertTrue(isinstance(target, QHBoxLayout))




    # sibling child addn works
    # higher child addn works
    # pruning of levels ds right when go back up
    # two top levels work
    # layouts created returned
    # addressing of obj works


_MOCK_LINE = 'mock line'
