from unittest import TestCase
from PySide.QtGui import QLabel, QPushButton, QWidget, \
    QLayout, qApp, QApplication

from objectfinder import ObjectFinder

class OtherThing(object):
    pass

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
        my_button = QPushButton()
        my_other_thing = OtherThing()
        base_class_filters = [QWidget, QLayout]
        finder = ObjectFinder(base_class_filters)
        found = finder.find_objects('QLabel', 'my_label')

        self.assertEquals(len(found), 1)
        found_object = found[0]
        self.assertEquals(found_object.__class__, QLabel)

