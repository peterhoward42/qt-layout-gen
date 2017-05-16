import os
from unittest import TestCase

from PySide.QtGui import QApplication, qApp

from qtlayoutbuilder.api.build import build_from_file


class FontsAndColorsTest(TestCase):
    """
    This class exercies the builder with a large variety of Qt widget and
    layout types.
    """

    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(FontsAndColorsTest, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists

    def test_coverage(self):
        file_path = os.path.abspath(
            os.path.join(__file__, "../../../../testdata/typography.txt"))
        layouts_created = build_from_file(file_path)

        widget = layouts_created.at('page')
        widget.show()

        qApp.exec_()
