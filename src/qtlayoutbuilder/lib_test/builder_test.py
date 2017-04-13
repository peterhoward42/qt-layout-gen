from unittest import TestCase

from PySide.QtGui import QHBoxLayout

from qtlayoutbuilder.api import LayoutError
from qtlayoutbuilder.lib.builder import Builder
from qtlayoutbuilder.lib_test import test_utils
from qtlayoutbuilder.lib_test.test_utils import \
    raises_layout_error_with_this_message


class TestBuilder(TestCase):

    # Test utilities and helpers, bottom up.

    #-------------------------------------------------------------------------
    # Assertions and error reporting.

    def test_assert_multiple_of_two(self):
        # Is silent when assertion succeeds.
        self.assertIsNone(Builder._assert_multiple_of_two(4, 'mock line'))

        # Is vociferous when assertion fails.
        result = raises_layout_error_with_this_message("""
            Indentation spaces must be a multiple of 2.
            This line: <mock line> is indented by 3 spaces.
            """,
            Builder._assert_multiple_of_two, 3, 'mock line')
        if not result:
            self.fail()

    def test_assert_no_tabs_present(self):
        # Is silent when assertion succeeds.
        self.assertIsNone(Builder._assert_no_tabs_present('no tabs here'))

        # Is vociferous when assertion fails.
        result = raises_layout_error_with_this_message("""
            This line: <	> contains a tab character -
            which is not allowed.
            """,
            Builder._assert_no_tabs_present, '\t')
        if not result:
            self.fail()

    #-------------------------------------------------------------------------
    # Minor functions

    def test_measure_indent(self):
        # Is silent when assertion succeeds.
        self.assertEquals(Builder._measure_indent('    foo'), 4)

        # Is vociferous when assertion fails.
        result = raises_layout_error_with_this_message("""
            Indentation spaces must be a multiple of 2.
            This line: <   foo> is indented by 3 spaces.
            """,
            Builder._measure_indent, '   foo')
        if not result:
            self.fail()

    def test_isolate_two_words(self):
        # Is silent when assertion succeeds.
        a,b = Builder._isolate_two_words('   foo   bar   ')
        self.assertEquals(a, 'foo')
        self.assertEquals(b, 'bar')

        # Is vociferous when assertion fails.
        result = raises_layout_error_with_this_message("""
            Cannot isolate two words from this line: <foo bar baz>,
            (after removal of comments and parenthesis).
            """,
            Builder._isolate_two_words, 'foo bar baz')
        if not result:
            self.fail()

    #-------------------------------------------------------------------------
    # API Level - wraps error with context properly.

    def test_context_added_to_error_messages(self):
        illegal_second_line = ('# a comment', '\t')

        result = raises_layout_error_with_this_message("""
            This line: <	> contains a tab character -
            which is not allowed.
            (Line number 2 of unit test)
            """,
            Builder.build, illegal_second_line, 'unit test')
        if not result:
            self.fail()

    #-------------------------------------------------------------------------
    # Trivial single child addition works.

    def xtest_simplest_possible_child_addition(self):
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
