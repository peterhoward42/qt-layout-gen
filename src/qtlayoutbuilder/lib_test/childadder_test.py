from unittest import TestCase

from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QWidget
from PySide.QtGui import qApp, QApplication, QPushButton, QLabel, QGridLayout, \
    QHBoxLayout, QStackedLayout, QStackedWidget, QTabWidget

from qtlayoutbuilder.api.filelocation import MOCK_FILELOCATION
from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib.childadder import ChildAdder
from qtlayoutbuilder.lib.inputtextrecord import InputTextRecord

from qtlayoutbuilder.test_utils import test_utils


class TestChildAdder(TestCase):
    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestChildAdder, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists

    def test_the_try_xxx_functions(self):
        # Try adding widgets (addWidget() - in true and false cases.
        self.assertTrue(
            ChildAdder._try_using_addWidget(QLabel(), QHBoxLayout()))
        self.assertFalse(ChildAdder._try_using_addWidget('foo', QHBoxLayout()))

        # Try adding widgets (addTab() - in true and false cases.
        self.assertTrue(ChildAdder._try_using_addTab(
            QLabel(), 'tab_label', QTabWidget()))
        self.assertFalse(ChildAdder._try_using_addTab(
            QLabel(), 'tab_label', QStackedWidget()))

        # Try adding layouts - in true and false cases.
        self.assertTrue(ChildAdder._try_using_addLayout(
            QVBoxLayout(), QHBoxLayout()))
        self.assertFalse(
            ChildAdder._try_using_addLayout(QLabel(), QHBoxLayout()))

    def test_add_widget_error_handling(self):
        try:
            ChildAdder._add_child_widget(
                'not a widget', 'arbitrary name',
                QHBoxLayout(), InputTextRecord.mock_record())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               This child name: <arbitrary name>, is a QWidget
               but neither addWidget(), nor addTab() worked
               on the parent object.,
            """, msg))

    def test_add_layout_error_handling(self):
        try:
            ChildAdder._add_child_layout(
                'not a layout', 'arbitrary name',
                QHBoxLayout(), InputTextRecord.mock_record())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                This child name: <arbitrary name>, is a QLayout
                but addLayout() did not work
                on the parent object.
            """, msg))

    def test_add_widget_working_properly(self):
        layout = QHBoxLayout()
        ChildAdder._add_child_widget(
            QLabel(), 'arbitrary name', layout, InputTextRecord.mock_record())
        self.assertEqual(layout.count(), 1)
        child = layout.itemAt(0)
        self.assertEqual(child.__class__.__name__, 'QWidgetItem')

    def test_add_child_text_error_handling(self):
        # Cannot setText() on a QWidget.
        try:
            ChildAdder._add_child_text('child_name', QWidget(),
                                       InputTextRecord.mock_record())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                Because this child name: <child_name>, is not defined
                anywhere else in your input as a QObject, we tried
                using it in a call to setText() on the parent.
                But this type of parent does not support setText().
            """, msg))

    def test_add_child_text_working_properly(self):
        # Can setText() on a QLabel
        label = QLabel()
        ChildAdder._add_child_text('child_name', label,
                                   InputTextRecord.mock_record())
        self.assertEqual(label.text(), 'child_name')

    def test_api_add_text_use_case_works(self):
        label = QLabel()
        empty_dict = {}
        ChildAdder.add_child_to_parent(
            'some_text', label, empty_dict, InputTextRecord.mock_record())
        self.assertEqual(label.text(), 'some_text')

    def test_api_add_widget_use_case_works(self):
        dict = {'my_label': QLabel()}
        layout = QVBoxLayout()
        ChildAdder.add_child_to_parent(
            'my_label', layout, dict, InputTextRecord.mock_record())
        self.assertEqual(layout.count(), 1)
        child = layout.itemAt(0)
        self.assertEqual(child.__class__.__name__, 'QWidgetItem')

    def test_api_add_layout_use_case_works(self):
        dict = {'my_layout': QHBoxLayout()}
        parent_layout = QVBoxLayout()
        ChildAdder.add_child_to_parent(
            'my_layout', parent_layout, dict, InputTextRecord.mock_record())
        self.assertEqual(parent_layout.count(), 1)
        child = parent_layout.itemAt(0)
        self.assertEqual(child.__class__.__name__, 'QHBoxLayout')
