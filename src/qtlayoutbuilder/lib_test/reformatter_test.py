from unittest import TestCase

from qtlayoutbuilder.lib.multiline_string_utils import MultilineString
from qtlayoutbuilder.lib.reformatter import ReFormatter


class TestReformatter(TestCase):

    def test_it(self):
        # The right column justification of this input is delibarately wild.
        str_input = """
            my_page                     QWidget
              layout QHBoxLayout
                label           QLabel(hello)
        """
        output = ReFormatter.format(str_input)
        output_for_comparison = MultilineString.get_as_left_shifted_lines(
            output)
        expected = MultilineString.get_as_left_shifted_lines("""
            my_page        QWidget
              layout       QHBoxLayout
                label      QLabel(hello)
        """)
        self.assertEqual(output_for_comparison, expected)
