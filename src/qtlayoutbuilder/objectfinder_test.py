from unittest import TestCase
from PySide.QtGui import QLabel, QPushButton, QWidget, \
    QLayout, qApp, QApplication, QHBoxLayout

from objectfinder import ObjectFinder

class OtherThing(object):

    def __init__(self):
        self.my_layout = QHBoxLayout()
        self.foo = 42

class TestObjectFinder(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        This test needs to be run in the context of a QApplication.
        :return: None
        """
        super(TestObjectFinder, cls).setUpClass()
        if qApp is None:
            QApplication([])

    def test_search_for_objects_finding_local_variable(self):
        # We create a local variable 'my_label' and then search for the object
        # it is pointing to.
        my_label = QLabel()
        my_button = QPushButton() # just to add to the search space
        base_class_filters = [QWidget, QLayout]
        finder = ObjectFinder(base_class_filters)

        found = finder.find_objects('my_label')
        self.assertEquals(len(found), 1)
        found_object = found[0]
        self.assertEquals(found_object.__class__, QLabel)

    def test_search_for_objects_finding_instance_attribute(self):
        # We instantiate an 'OtherThing' and search for an object that is
        # pointed to by the 'my_layout' attribute of that OtherThing.

        # We are NOT searching for the 'other thing' itself, but for
        # a QLayout object that 'other thing' refers to  with one of its
        # attributes that is named 'my_layout. In other words we are searching
        # for the the layout pointed to by other_thing.my_layout
        other_thing = OtherThing()
        my_button = QPushButton() # just to add to the search space
        base_class_filters = [QWidget, QLayout]
        finder = ObjectFinder(base_class_filters)

        found = finder.find_objects('my_layout')
        self.assertEquals(len(found), 1)
        found_object = found[0]
        self.assertEquals(found_object.__class__, QHBoxLayout)
