import os
from unittest import TestCase

from PySide.QtGui import QApplication, qApp
from qtlayoutbuilder.api.build import build_from_file


class TestCoverage(TestCase):
    """
    This class exercies the builder with a large variety of Qt widget and
    layout types.
    """

    def test_coverage(self):
        try:
            QApplication([])
        except RuntimeError:
            pass # Singleton already exists.

        file_path = os.path.abspath(
                os.path.join(__file__,
                        "../../../../testdata/coverage_example.txt"))
        layouts_created = build_from_file(file_path)
        widget = layouts_created.get_element('page')
        widget.show()
        qApp.exec_()
