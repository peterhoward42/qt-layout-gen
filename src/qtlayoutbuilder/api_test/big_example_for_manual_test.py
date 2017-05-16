import os
from unittest import TestCase

from PySide.QtGui import QApplication, qApp

from qtlayoutbuilder.api.build import build_from_file


class TestBigExampleForManual(TestCase):
    # Make sure the example used for the manual is viable.
    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestBigExampleForManual, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists

    def test_big_example(self):
        file_path = os.path.abspath(
            os.path.join(
                __file__,
                "../../../../testdata/big_example_for_manual.txt"))
        layouts_created = build_from_file(file_path)

        widget = layouts_created.at('page')
        widget.show()

        #qApp.exec_()
