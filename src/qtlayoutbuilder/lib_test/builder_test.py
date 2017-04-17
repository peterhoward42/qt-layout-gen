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

    def test_error_message_when_tabs_are_present(self):
        input = """
            page        \t QLabel
        """
        result = raises_layout_error_with_this_message("""
                This line contains a tab - which is not allowed.
                (This line: <page        \t QLabel>)
                (Line number: 1, from unit test provenance)
            """,
                Builder.build, input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_indent_is_not_multiple_of_two(self):
        input = """
            page        QLabel
             layout     QHBoxLayout
        """
        result = raises_layout_error_with_this_message("""
                A line is indented by 1 spaces.
                Indentation spaces must be a multiple of 2.
                (This line: < layout     QHBoxLayout>)
                (Line number: 2, from unit test provenance)
            """,
                Builder.build, input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_too_many_words_per_line(self):
        input = """
            page        QLabel  QLabel
        """
        result = raises_layout_error_with_this_message("""
            Cannot split this line, into exactly two words,
            (after comments and parenthesis have been removed.)
            (This line: <page        QLabel  QLabel>)
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
            Cannot split this line, into exactly two words,
            (after comments and parenthesis have been removed.)
            (This line: <page>)
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
            This line is indented too much.
            It cannot be indented relative to the line
            above it by more than 2 spaces.
            (This line: <    layout    QVBoxLayout>)
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
            Cannot do anything with the text you specified
            in parenthesis because the object being created
            has neither the setText(), nor the setTitle() method.
            (This line: <layout      QVBoxLayout(hello)>)
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

    def test_adding_text_works_using_set_text_works(self):
        input = """
            label       QLabel(hello)
        """
        layouts_created = Builder.build(input, 'unit test provenenance')
        widget = layouts_created.get_element('label')
        self.assertEqual(widget.text(), 'hello')

    def test_adding_text_works_using_set_title(self):
        input = """
            group       QGroupBox(hello)
        """
        layouts_created = Builder.build(input, 'unit test provenenance')
        widget = layouts_created.get_element('group')
        self.assertEqual(widget.title(), 'hello')


_MOCK_LINE = 'mock line'
