from unittest import TestCase
from PySide.QtGui import QLabel, QHBoxLayout, qApp, QApplication

from widgetandlayoutfinder import WidgetAndLayoutFinder

class HasBox(object):
    """Has attribute 'fibble' pointing to a QVBoxLayout"""
    def __init__(self):
        self.fibble = QHBoxLayout()

class HasLabel(object):
    """Has attribute 'fibble' pointing to a QLabel"""
    def __init__(self):
        self.fibble = QLabel()

class TestWidgetAndLayoutFinder(TestCase):

    def setUp(self):
        super(TestWidgetAndLayoutFinder, self).setUp()
        if qApp is None:
            QApplication([])

    def test_search_for_widget(self):

        # Discriminates on particular class and succeeds in finding
        # target.

        # Both of the classes instantiated here have an attribute 'fibble' which
        # points to a QLayout or a QWidget, but only one is the particular class
        # we will target with our search.
        contains_target_name_a = HasBox()
        contains_target_name_b = HasLabel()

        finder = WidgetAndLayoutFinder()
        found = finder.find(QLabel, 'fibble')
        self.assertEquals(len(found), 1)
        found_object = found[0]
        self.assertEquals(found_object, contains_target_name_b.fibble)
