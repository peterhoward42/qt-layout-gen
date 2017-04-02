import sys
import os.path

from unittest import TestCase

from PySide.QtGui import qApp, QApplication, QWidget

from qtlayoutbuilder.api.api import LayoutBuilder


class TestRealisticExample(TestCase):

    def test_realist_example(self):
        """
        This test demonstrates a realistic - complex GUI case.
        """
        try:
            QApplication([])
        except RuntimeError:
            pass # Singleton already exists.

        dir = os.path.abspath(
            os.path.join(__file__, "../../../../testdata/realistic_example"))

        layouts = LayoutBuilder.build_layouts_from_dir(dir)

        widget = QWidget()
        top_level_layout = layouts.layout_element['top_level']
        widget.setLayout(top_level_layout)
        widget.show()

        qApp.exec_()
