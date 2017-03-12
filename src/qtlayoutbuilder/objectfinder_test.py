from unittest import TestCase
from PySide.QtGui import QLabel, QHBoxLayout, qApp, QApplication

from objectfinder import ObjectFinder, find_qobject_instances

class TestObjectFinder(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        We need to create (or reuse) a QApplication before we instantiate
        any QWidget objects - or Qt emits warnings to the console.
        :return: None
        """
        super(TestObjectFinder, cls).setUpClass()
        if qApp is None:
            QApplication([])

    def test_search_for_objects(self):
        my_label = QLabel()
        found_objects = find_qobject_instances('QLabel', 'my_label')

        self.assertEquals(len(found_objects), 1)
        found_object = found_objects[0]
        self.assertEquals(found_object.__class__, FindMe)

