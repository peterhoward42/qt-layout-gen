from unittest import TestCase

from PySide.QtCore import Qt
from PySide.QtGui import QApplication, QHBoxLayout, QLabel, QScrollArea, \
    QSlider, QSpacerItem, QStackedWidget, QTabWidget, QVBoxLayout, QWidget

from qtlayoutbuilder.lib.childadder import ChildAdder
from qtlayoutbuilder.lib_test.test_utils import \
    raises_layout_error_with_this_message


class TestChildAdder(TestCase):
    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestChildAdder, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists

    def test_error_handling_when_speculative_methods_all_fail(self):
        # There is no way to add a widget to a widget.
        result = raises_layout_error_with_this_message("""
            Could not add this child: <fred> to its parent.
            The child is a: <QWidget>
            The parent is a: <QWidget>

            None of the following addition methods worked:

            addLayout
            setLayout
            addWidget
            addTab
            setWidget
            addSpacerItem
        """, ChildAdder.add, QWidget(), 'fred', QWidget())
        if not result:
            self.fail()

    def test_add_layout_succeeding(self):
        parent = QVBoxLayout()
        ChildAdder.add(QHBoxLayout(), 'fred', parent)
        self.assertEqual(parent.count(), 1)
        self.assertTrue(isinstance(parent.itemAt(0), QHBoxLayout))

    def test_set_layout_succeeding(self):
        parent = QWidget()
        ChildAdder.add(QHBoxLayout(), 'fred', parent)
        self.assertTrue(isinstance(parent.layout(), QHBoxLayout))

    def test_add_widget_succeeding(self):
        parent = QStackedWidget()
        ChildAdder.add(QLabel(), 'fred', parent)
        self.assertEqual(parent.count(), 1)
        self.assertTrue(isinstance(parent.currentWidget(), QLabel))

    def test_add_tab_succeeding(self):
        parent = QTabWidget()
        ChildAdder.add(QLabel(), 'fred', parent)
        self.assertEqual(parent.count(), 1)
        self.assertTrue(isinstance(parent.currentWidget(), QLabel))

    def test_set_widget_succeeding(self):
        parent = QScrollArea()
        ChildAdder.add(QLabel(), 'fred', parent)
        self.assertTrue(isinstance(parent.widget(), QLabel))
        # We promise to setWidgetResizable(True), also.
        resizable = parent.widgetResizable()
        self.assertTrue(resizable)

    def test_add_spacer_item_succeeding(self):
        parent = QHBoxLayout()
        ChildAdder.add(QSpacerItem(0, 0), 'fred', parent)
        self.assertTrue(isinstance(parent.itemAt(0), QSpacerItem))

    def test_qslider_intervention(self):
        parent = QHBoxLayout()
        slider = QSlider()  # Don't specify orientation.
        ChildAdder.add(slider, 'fred', parent)
        # We promise to give it horizontal (the non-default) orientation.
        orient = slider.orientation()
        self.assertEqual(orient, Qt.Orientation.Horizontal)
