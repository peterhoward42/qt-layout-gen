from unittest import TestCase

from PySide.QtGui import QApplication
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QWidget

from qtlayoutbuilder.lib.builder import Builder
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString
from qtlayoutbuilder.lib_test.test_utils import \
    raises_layout_error_with_this_message


class TestBuilder(TestCase):

    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestBuilder, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass # Singleton already exists

    #-------------------------------------------------------------------------
    # Test utilities and helpers, bottom up first to make sure we can
    # rely on what they say when debugging problems from higher level tests.

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

    def test_error_message_when_too_many_words_per_line(self):
        input = """
            page        QLabel  QLabel
        """
        result = raises_layout_error_with_this_message("""
            Cannot split this line: <page        QLabel  QLabel>,
            into exactly two words,
            (after comments and parenthesis have been removed.)
            (Line number: 1, from unit test provenance)
            """,
            Builder.build, input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_too_few_words_per_line(self):
        input = """
            page
        """
        result = raises_layout_error_with_this_message("""
                Cannot split this line: <page>,
                into exactly two words,
                (after comments and parenthesis have been removed.)
                (Line number: 1, from unit test provenance)
            """,
            Builder.build, input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_skip_indent_levels(self):
        input = """
            page        QWidget
                layout    QVBoxLayout
        """
        result = raises_layout_error_with_this_message("""
                This line is indented too much: <    layout    QVBoxLayout>.
                It cannot be indented relative to the line
                above it by more than 2 spaces.
                (Line number: 2, from unit test provenance)
            """,
            Builder.build, input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_no_meaningful_input_found(self):
        input = """
            # Hello
        """
        result = raises_layout_error_with_this_message("""
                This input provided (unit test provenance) contains nothing, or
                nothing except whitespace and comments.
            """,
                Builder.build, input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_set_text_fails(self):
        # You can't call setText('hello') on a QVBoxLayout.
        input = """
            layout      QVBoxLayout(hello)
        """
        result = raises_layout_error_with_this_message("""
            The attempt to call setText() with your parenthesised text
            from this line: <layout      QVBoxLayout(hello)> failed.
            The underlying error reported was:
            <'PySide.QtGui.QVBoxLayout' object has no attribute 'setText'>.
            (Line number: 1, from unit test provenance)
            """,
                Builder.build, input, 'unit test provenance')
        if not result:
            self.fail()

    #-------------------------------------------------------------------------
    # API Level

    #-------------------------------------------------------------------------
    # Simplest possible input.

    def test_simplest_possible_runs_without_crashing(self):
        input = """
            page        QWidget
              layout    QVBoxLayout
        """
        layouts_created = Builder.build(input, 'unit test provenenance')

    def test_simplest_possible_dump_of_contents_is_correct(self):
        input = """
            page        QWidget
              layout    QVBoxLayout
        """
        layouts_created = Builder.build(input, 'unit test provenenance')
        dumped = MultilineString.normalise(layouts_created.dump())
        expected = MultilineString.normalise("""
            page           QWidget
            page.layout    QVBoxLayout
        """)
        self.assertEqual(dumped, expected)

    def test_simplest_possible_querying_accessor_works(self):
        input = """
            page        QWidget
              layout    QVBoxLayout
        """
        layouts_created = Builder.build(input, 'unit test provenenance')
        page = layouts_created.get_element('page')
        self.assertTrue(isinstance(page, QWidget))

    def test_simplest_possible_creates_parent_child_relations(self):
        input = """
            page        QWidget
              layout    QVBoxLayout
        """
        layouts_created = Builder.build(input, 'unit test provenenance')
        page = layouts_created.get_element('page')
        self.assertTrue(isinstance(page.layout(), QVBoxLayout))

    def test_sibling_child_additions_work(self):
        input = """
            layout      QVBoxLayout
              a         QLabel
              b         QLabel
              c         QLabel
        """
        layouts_created = Builder.build(input, 'unit test provenenance')
        dumped = MultilineString.normalise(layouts_created.dump())
        expected = MultilineString.normalise("""
            layout      QVBoxLayout
            layout.a    QLabel
            layout.b    QLabel
            layout.c    QLabel
        """)
        layout = layouts_created.get_element('layout')
        self.assertEqual(layout.count(), 3)

    def test_multi_level_descent_works(self):
        input = """
            page          QWidget
              layout      QVBoxLayout
                a         QLabel
                b         QLabel
                c         QLabel
        """
        layouts_created = Builder.build(input, 'unit test provenenance')
        dumped = MultilineString.normalise(layouts_created.dump())
        expected = MultilineString.normalise("""
            page             QWidget
            page.layout      QVBoxLayout
            page.layout.a    QLabel
            page.layout.b    QLabel
            page.layout.c    QLabel
        """)
        self.assertEqual(dumped, expected)

    def test_multi_level_descent_and_ascent_works(self):
        input = """
            page          QWidget
              layout      QVBoxLayout
                a         QLabel
                b         QLabel
                fred      QWidget
                  layout  QHBoxLayout
                    lbl   QLabel
                c         QLabel
        """
        layouts_created = Builder.build(input, 'unit test provenenance')
        dumped = MultilineString.normalise(layouts_created.dump())
        expected = MultilineString.normalise("""
            page                           QWidget
            page.layout                    QVBoxLayout
            page.layout.a                  QLabel
            page.layout.b                  QLabel
            page.layout.fred               QWidget
            page.layout.fred.layout        QHBoxLayout
            page.layout.fred.layout.lbl    QLabel
            page.layout.c                  QLabel
        """)
        self.assertEqual(dumped, expected)
        layout = layouts_created.get_element('page.layout')
        self.assertEqual(layout.count(), 4)

    def test_more_than_one_top_level_object_works(self):
        input = """
            page1         QWidget
              layout      QVBoxLayout
            page2         QWidget
              layout      QVBoxLayout
        """
        layouts_created = Builder.build(input, 'unit test provenenance')
        dumped = MultilineString.normalise(layouts_created.dump())
        expected = MultilineString.normalise("""
            page1           QWidget
            page1.layout    QVBoxLayout
            page2           QWidget
            page2.layout    QVBoxLayout
        """)
        self.assertEqual(dumped, expected)
        widget = layouts_created.get_element('page2')
        self.assertTrue(isinstance(widget.layout(), QVBoxLayout))

    def test_adding_text_works_for_relevant_types(self):
        input = """
            label       QLabel(hello)
            button      QPushButton(hello)
            lineedit    QLineEdit(hello)
        """
        layouts_created = Builder.build(input, 'unit test provenenance')


_MOCK_LINE = 'mock line'
