from unittest import TestCase

from PySide.QtGui import qApp, QApplication, QPushButton, QLabel, QGridLayout, \
    QHBoxLayout, QStackedLayout, QStackedWidget, QTabWidget

from qtlayoutbuilder.lib.childadder import add_child_to_parent

class TestChildAdder(TestCase):

    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestChildAdder, cls).setUpClass()
        if qApp is None:
            QApplication([])

    def test_unsupported_type_combo_error_handling(self):
        self.assertRaises(
            NotImplementedError,
            add_child_to_parent, QPushButton(), QLabel())

    def test_all_supported_combinations_dont_crash(self):
        add_child_to_parent(QGridLayout(), QHBoxLayout())
        add_child_to_parent(QLabel(), QHBoxLayout())
        add_child_to_parent(QLabel(), QStackedLayout())
        add_child_to_parent(QLabel(), QStackedWidget())
        add_child_to_parent(QLabel(), QTabWidget())
        add_child_to_parent('foo', QPushButton())
        add_child_to_parent('foo', QLabel())


