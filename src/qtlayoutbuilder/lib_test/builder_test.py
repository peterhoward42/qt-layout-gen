from unittest import TestCase

from PySide.QtGui import QHBoxLayout

from qtlayoutbuilder.lib.builder import Builder
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

    def test_assert_is_two_words(self):
        # Is silent when assertion succeeds.
        self.assertIsNone(Builder._assert_is_two_words(
                ('foo', 'bar'), _MOCK_LINE))

        # Is vociferous when assertion fails.
        result = raises_layout_error_with_this_message("""
            Cannot split this line: <mock line>,
            into exactly two words,
            (after comments and parenthesis have been removed.)
            """,
            Builder._assert_is_two_words, ('foo'), _MOCK_LINE)
        if not result:
            self.fail()

    #-------------------------------------------------------------------------
    # Minor functions

    #-------------------------------------------------------------------------
    # API Level

    #-------------------------------------------------------------------------
    # Trivial single child addition works.

    def test_simplest_possible_input(self):
        input = """
            page        widget
              layout    vbox
        """
        created = Builder.build(input, 'unit test provenenance')




    # sibling child addn works
    # higher child addn works
    # pruning of levels ds right when go back up
    # two top levels work
    # layouts created returned
    # addressing of obj works


_MOCK_LINE = 'mock line'
