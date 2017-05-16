import os
from unittest import TestCase

from PySide.QtGui import QApplication, qApp

from qtlayoutbuilder.api.build import build_from_file


class TestCoverage(TestCase):
    """
    This class exercies the builder with a large variety of Qt widget and
    layout types. And prints out a uniqued and sorted list of each Qt Type
    used.
    """

    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestCoverage, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists

    def test_coverage(self):
        file_path = os.path.abspath(
            os.path.join(
                __file__,
                "../../../../testdata/coverage_example.txt"))
        layouts_created = build_from_file(file_path)

        lines = layouts_created._impl.dump().split('\n')
        qwords = [line.split().pop() for line in lines]
        qwords = set(qwords)
        qwords = sorted(qwords)
        for w in qwords:
            print w

        widget = layouts_created.at('page')
        widget.show()

        # dialog = layouts_created.get_element('my_dialog')
        # dialog.exec_()

        #qApp.exec_()
