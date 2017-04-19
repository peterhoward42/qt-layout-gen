import os
import shutil
import tempfile
from unittest import TestCase

from PySide.QtGui import QApplication, qApp
from os import path

from qtlayoutbuilder.api.build import build_from_multi_line_string, \
    build_from_file
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString


class TestApiBasics(TestCase):
    """
    This class tests the API entry-point functions are viable and not much
    else. The API functions delegate all their meaningful work to an
    implementation class - which has its own more comprehensive tests.
    """

    def test_build_from_multiline_string_works(self):
        try:
            QApplication([])
        except RuntimeError:
            pass # Singleton already exists.


        input = """
            my_page         QWidget
              layout        QVBoxLayout
                foo         QPushButton
                bar         QPushButton
        """
        layouts_created = build_from_multi_line_string(input)
        widget = layouts_created.get_element('my_page')
        widget.show()
        #qApp.exec_()

    def test_build_from_file(self):
        try:
            QApplication([])
        except RuntimeError:
            pass # Singleton already exists.

        file_path = os.path.abspath(
            os.path.join(__file__, "../../../../testdata/tiny_example.txt"))
        layouts_created = build_from_file(file_path)
        widget = layouts_created.get_element('my_page')
        widget.show()
        #qApp.exec_()

    def test_reformatted_file_gets_written_to_file_specified(self):
        tmp_dir = tempfile.mkdtemp()
        reformat_location = path.join(tmp_dir, 're-formatted.txt')
        print 'xxxxxxx %s' % reformat_location

        try:
            QApplication([])
        except RuntimeError:
            pass # Singleton already exists.
        input = """
            my_page         QWidget
              layout                QVBoxLayout
        """
        layouts_created = build_from_multi_line_string(
            input, auto_format_and_write_to=reformat_location)

        with open(reformat_location, 'r') as input_file:
            contents = MultilineString.shift_left(input_file.read())

        self.assertEqual(contents, MultilineString.shift_left("""
        my_page       QWidget
          layout      QVBoxLayout
        """))

        shutil.rmtree(tmp_dir)
