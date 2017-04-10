from unittest import TestCase

from PySide.QtGui import QFrame
from PySide.QtGui import QVBoxLayout
from PySide.QtGui import QWidget
from PySide.QtGui import qApp, QApplication, QLabel, QHBoxLayout, \
    QStackedWidget, QTabWidget

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

    def test_add_child_text_substitutes_double_underscores(self):
        label = QLabel()
        ChildAdder._add_child_text('This__should__get__spaces', label,
                InputTextRecord.mock_record())
        self.assertEqual(label.text(), 'This should get spaces')

    def test_api_add_text_use_case_works(self):
        label = QLabel()
        empty_dict = {}
        ChildAdder.add_child_to_parent(
            'some_text', label, empty_dict, InputTextRecord.mock_record())
        self.assertEqual(label.text(), 'some_text')

    def test_add_layout_succeeding(self):
        parent = QVBoxLayout()
        child_lookup = {'child_layout': QHBoxLayout()}
        ChildAdder.add_child_to_parent(
                'child_layout', parent, child_lookup,
                InputTextRecord.mock_record())
        self.assertEqual(parent.count(), 1)
        self.assertTrue(isinstance(parent.itemAt(0), QHBoxLayout))

    def test_set_layout_succeeding(self):
        parent = QWidget()
        child_lookup = {'child_layout': QHBoxLayout()}
        ChildAdder.add_child_to_parent(
                'child_layout', parent, child_lookup,
                InputTextRecord.mock_record())
        self.assertTrue(isinstance(parent.layout(), QHBoxLayout))

    def test_add_widget_succeeding(self):
        parent = QStackedWidget()
        child_lookup = {'child_widget': QLabel()}
        ChildAdder.add_child_to_parent(
                'child_widget', parent, child_lookup,
                InputTextRecord.mock_record())
        self.assertEqual(parent.count(), 1)
        self.assertTrue(isinstance(parent.currentWidget(), QLabel))
