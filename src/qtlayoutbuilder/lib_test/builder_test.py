from unittest import TestCase

from PySide.QtGui import QApplication, QPushButton, QVBoxLayout

from qtlayoutbuilder.lib.builder import Builder
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString
from qtlayoutbuilder.lib_test.test_utils import \
    raises_layout_error_with_this_message, \
    raises_layout_error_with_this_approximately_this_message


class TestBuilder(TestCase):
    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestBuilder, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists

    # -------------------------------------------------------------------------
    # Test utilities and helpers, bottom up first to make sure we can
    # rely on what they say when debugging problems from higher level tests.

    # -------------------------------------------------------------------------
    # Assertions and error reporting.

    def test_error_message_when_tabs_are_present(self):
        str_input = """
            page        \t QLabel
        """
        result = raises_layout_error_with_this_message("""
                This line contains a tab - which is not allowed.
                (This line: <page        \t QLabel>)
                (Line number: 1, from unit test provenance)
            """, Builder.build, str_input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_indent_is_not_multiple_of_two(self):
        str_input = """
            page        QLabel
             layout     QHBoxLayout
        """
        result = raises_layout_error_with_this_message("""
                A line is indented by 1 spaces.
                Indentation spaces must be a multiple of 2.
                (This line: < layout     QHBoxLayout>)
                (Line number: 2, from unit test provenance)
            """, Builder.build, str_input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_too_many_words_per_line(self):
        str_input = """
            page        QLabel  QLabel
        """
        result = raises_layout_error_with_this_message("""
            Cannot split this line, into exactly two words,
            (after comments and parenthesis have been removed.)
            (This line: <page        QLabel  QLabel>)
            (Line number: 1, from unit test provenance)
            """, Builder.build, str_input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_too_few_words_per_line(self):
        str_input = """
            page
        """
        result = raises_layout_error_with_this_message("""
            Cannot split this line, into exactly two words,
            (after comments and parenthesis have been removed.)
            (This line: <page>)
            (Line number: 1, from unit test provenance)
            """, Builder.build, str_input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_skip_indent_levels(self):
        str_input = """
            page        QWidget
                layout    QVBoxLayout
        """
        result = raises_layout_error_with_this_message("""
            This line is indented too much.
            It cannot be indented relative to the line
            above it by more than 2 spaces.
            (This line: <    layout    QVBoxLayout>)
            (Line number: 2, from unit test provenance)
            """, Builder.build, str_input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_no_meaningful_input_found(self):
        str_input = """
            # Hello
        """
        result = raises_layout_error_with_this_message("""
                This input provided (unit test provenance) contains nothing, or
                nothing except whitespace and comments.
            """, Builder.build, str_input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_set_text_fails(self):
        # You can't call setText('hello') on a QVBoxLayout.
        str_input = """
            layout      QVBoxLayout(hello)
        """
        result = raises_layout_error_with_this_message("""
            Cannot do anything with the text you specified
            in parenthesis because the object being created
            has neither of the following methods: setText(), or setTitle().
            (This line: <layout      QVBoxLayout(hello)>)
            (Line number: 1, from unit test provenance)
            """, Builder.build, str_input, 'unit test provenance')
        if not result:
            self.fail()

    def test_error_message_when_name_is_not_unique(self):
        # Names must be unique.
        str_input = """
            foo      QVBoxLayout
              bar    QGroupBox
              bar    QLabel
        """
        result = raises_layout_error_with_this_message("""
            The name you have given this item (<bar>), has already
            been used.
            (This line: <  bar    QLabel>)
            (Line number: 3, from unit test provenance)
            """, Builder.build, str_input, 'unit test provenance')
        if not result:
            self.fail()

    # -------------------------------------------------------------------------
    # API Level

    # -------------------------------------------------------------------------
    # Simplest possible input.

    def test_simplest_possible_runs_without_crashing(self):
        str_input = """
            page        QWidget
              layout    QVBoxLayout
        """
        Builder.build(str_input, 'unit test provenenance')

    def test_simplest_possible_dump_of_contents_is_correct(self):
        str_input = """
            page        QWidget
              layout    QVBoxLayout
        """
        layouts_created = Builder.build(str_input, 'unit test provenenance')
        dumped = MultilineString.normalise(layouts_created.dump())
        expected = MultilineString.normalise("""
            page           QWidget
            page.layout    QVBoxLayout
        """)
        self.assertEqual(dumped, expected)

    def test_querying_accessor_normal_working(self):
        str_input = """
            layout       QVBoxLayout
              foo_n1     QLabel
              foo_n2     QPushButton
              foo_n3     QTextEdit
        """
        layouts_created = Builder.build(str_input, 'unit test provenenance')
        found = layouts_created.at('foo_n2')
        self.assertTrue(isinstance(found, QPushButton))

    def test_querying_accessor_error_msg_for_none_found(self):
        str_input = """
            layout       QVBoxLayout
              foo        QLabel
              bar        QPushButton
              baz        QTextEdit
        """
        layouts_created = Builder.build(str_input, 'unit test provenance')
        result = raises_layout_error_with_this_message("""
            No path can be found that ends with <harry>.
            These are the paths that do exist:

            layout        QVBoxLayout
            layout.foo    QLabel
            layout.bar    QPushButton
            layout.baz    QTextEdit
        """, layouts_created.at, 'harry')
        if not result:
            self.fail()

    def test_simplest_possible_creates_parent_child_relations(self):
        str_input = """
            page        QWidget
              layout    QVBoxLayout
        """
        layouts_created = Builder.build(str_input, 'unit test provenenance')
        page = layouts_created.at('page')
        self.assertTrue(isinstance(page.layout(), QVBoxLayout))

    def test_sibling_child_additions_work(self):
        str_input = """
            layout      QVBoxLayout
              a         QLabel
              b         QLabel
              c         QLabel
        """
        layouts_created = Builder.build(str_input, 'unit test provenenance')
        MultilineString.normalise(layouts_created.dump())
        layout = layouts_created.at('layout')
        self.assertEqual(layout.count(), 3)

    def test_multi_level_descent_works(self):
        str_input = """
            page          QWidget
              layout      QVBoxLayout
                a         QLabel
                b         QLabel
                c         QLabel
        """
        layouts_created = Builder.build(str_input, 'unit test provenenance')
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
        str_input = """
            page           QWidget
              vlayout      QVBoxLayout
                a          QLabel
                b          QLabel
                fred       QWidget
                  hlayout  QHBoxLayout
                    lbl    QLabel
                c          QLabel
        """
        layouts_created = Builder.build(str_input, 'unit test provenenance')
        dumped = MultilineString.normalise(layouts_created.dump())
        expected = MultilineString.normalise("""
            page                             QWidget
            page.vlayout                     QVBoxLayout
            page.vlayout.a                   QLabel
            page.vlayout.b                   QLabel
            page.vlayout.fred                QWidget
            page.vlayout.fred.hlayout        QHBoxLayout
            page.vlayout.fred.hlayout.lbl    QLabel
            page.vlayout.c                   QLabel
        """)
        self.assertEqual(dumped, expected)
        layout = layouts_created.at('vlayout')
        self.assertEqual(layout.count(), 4)

    def test_more_than_one_top_level_object_works(self):
        str_input = """
            page1          QWidget
              layout1      QVBoxLayout
            page2          QWidget
              layout2      QVBoxLayout
        """
        layouts_created = Builder.build(str_input, 'unit test provenenance')
        dumped = MultilineString.normalise(layouts_created.dump())
        expected = MultilineString.normalise("""
            page1            QWidget
            page1.layout1    QVBoxLayout
            page2            QWidget
            page2.layout2    QVBoxLayout
        """)
        self.assertEqual(dumped, expected)
        widget = layouts_created.at('page2')
        self.assertTrue(isinstance(widget.layout(), QVBoxLayout))

    def test_adding_text_unicode_decode_works(self):
        str_input = """
            page        QWidget
              layout    QHBoxLayout
                label       QLabel(\u25c0)
        """
        layouts_created = Builder.build(str_input, 'unit test provenenance')
        label = layouts_created.at('label')
        txt = label.text()
        self.assertEqual(txt, u'\u25c0')

    def test_adding_text_unicode_decode_error_reporting(self):
        # The \u encoded unicode code-point, has only 3 ascii characters
        # following. Well formed needs 4.
        str_input = """
            page        QWidget
              layout    QHBoxLayout
                label       QLabel(\u25c)
        """
        # Use the approx test, because the python exception is a long line
        # and gets messed up with auto reformat of the source.
        result = raises_layout_error_with_this_approximately_this_message("""
            Python raised an exception when the builder tried to
            deal with unicode encoded values in your text: <\u25c>. The
            underlying python error was:
            'rawunicodeescape' codec can't decode bytes in position 
            0-4: truncated \uXXXX
            (This line: <    label       QLabel(\u25c) >)
            (Line number: 3, from unit test provenance)
            """, Builder.build, str_input, 'unit test provenance')
        if not result:
            self.fail()

    def test_adding_text_works_using_set_text_works(self):
        str_input = """
            label       QLabel(hello)
        """
        layouts_created = Builder.build(str_input, 'unit test provenenance')
        widget = layouts_created.at('label')
        self.assertEqual(widget.text(), 'hello')

    def test_adding_text_works_using_set_title(self):
        str_input = """
            group       QGroupBox(hello)
        """
        layouts_created = Builder.build(str_input, 'unit test provenenance')
        widget = layouts_created.at('group')
        self.assertEqual(widget.title(), 'hello')


_MOCK_LINE = 'mock line'
