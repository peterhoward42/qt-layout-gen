import os
from unittest import TestCase

from PySide.QtGui import QApplication, qApp
from qtlayoutbuilder.api.build import build_from_multi_line_string, \
    build_from_file


class TestBuilderApi(TestCase):
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
            my_page         widget
              layout        vbox
                foo         button
                bar         button
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
