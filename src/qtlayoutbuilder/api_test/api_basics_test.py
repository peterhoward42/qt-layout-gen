import os
import shutil
import tempfile
from os import path
from unittest import TestCase

from PySide.QtGui import QApplication

from qtlayoutbuilder.api.build import build_from_file, \
    build_from_multi_line_string
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString


class TestApiBasics(TestCase):
    """
    This class tests the API entry-point functions are viable and not much
    else. The API functions delegate all their meaningful work to an
    implementation class - which has its own more comprehensive tests.
    """

    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestApiBasics, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists

    def test_build_from_multiline_string_works(self):

        str_input = """
            my_page         QWidget
              layout        QVBoxLayout
                foo         QPushButton
                bar         QPushButton
        """
        layouts_created = build_from_multi_line_string(str_input)
        widget = layouts_created.at('my_page')
        widget.show()
        # qApp.exec_()

    def test_build_from_file_works(self):

        file_path = os.path.abspath(
            os.path.join(__file__, "../../../../testdata/tiny_example.txt"))
        layouts_created = build_from_file(file_path)
        widget = layouts_created.at('top_widget')
        widget.show()
        # qApp.exec_()

    def test_reformatted_file_gets_written_to_file_specified(self):

        tmp_dir = tempfile.mkdtemp()
        reformat_location = path.join(tmp_dir, 're-formatted.txt')

        str_input = """
            top_widget         QWidget
              layout                QVBoxLayout
        """
        build_from_multi_line_string(
            str_input, auto_format_and_write_to=reformat_location)

        with open(reformat_location, 'r') as input_file:
            contents = MultilineString.shift_left(input_file.read())

        print contents
        self.assertEqual(contents, MultilineString.shift_left("""
            top_widget      QWidget
              layout        QVBoxLayout
        """))

        shutil.rmtree(tmp_dir)
