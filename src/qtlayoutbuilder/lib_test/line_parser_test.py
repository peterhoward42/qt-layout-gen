from unittest import TestCase
from qtlayoutbuilder.lib.line_parser import LineParser
from qtlayoutbuilder.lib_test.test_utils import \
    raises_layout_error_with_this_message


class TestLineParser(TestCase):
    def test_recognizes_comments(self):
        is_a_comment, is_blank, indent, name, type_string, parenthesised = \
            LineParser.parse_line(
                '    # foo bar')
        self.assertEqual(is_a_comment, True)

    def test_recognizes_blank(self):
        is_a_comment, is_blank, indent, name, type_string, parenthesised = \
            LineParser.parse_line(
                '    ')
        self.assertEqual(is_blank, True)

    def test_on_legit_line(self):
        is_a_comment, is_blank, indent, name, type_string, parenthesised = \
            LineParser.parse_line(
                '    fred    QLabel(hello)')
        self.assertEqual(is_a_comment, False)
        self.assertEqual(indent, 4)
        self.assertEqual(name, 'fred')
        self.assertEqual(type_string, 'QLabel')
        self.assertEqual(parenthesised, 'hello')

    def test_error_message_when_indent_is_not_multiple_of_two(self):
        result = raises_layout_error_with_this_message("""
                A line is indented by 3 spaces.
                Indentation spaces must be a multiple of 2.
            """, LineParser.parse_line, '   foo')
        if not result:
            self.fail()

    def test_error_message_when_too_many_words_per_line(self):
        result = raises_layout_error_with_this_message("""
            Cannot split this line, into exactly two words,
           (after comments and parenthesis have been removed.)
            """, LineParser.parse_line, 'foo bar baz')
        if not result:
            self.fail()

    def test_error_message_when_too_few_words_per_line(self):
        result = raises_layout_error_with_this_message("""
            Cannot split this line, into exactly two words,
            (after comments and parenthesis have been removed.)
            """, LineParser.parse_line, 'foo')
        if not result:
            self.fail()

    def test_error_message_when_tab_is_present(self):
        result = raises_layout_error_with_this_message("""
                This line contains a tab - which is not allowed.
            """, LineParser.parse_line, '\t')
        if not result:
            self.fail()

    def test_error_message_when_something_comes_after_parenthesis(self):
        result = raises_layout_error_with_this_message("""
            This line contains something after the parenthesis, which is not
            allowed.    
            """, LineParser.parse_line, '    foo   QLabel(hello)X')
        if not result:
            self.fail()
