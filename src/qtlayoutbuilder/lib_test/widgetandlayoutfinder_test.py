from unittest import TestCase

from PySide.QtGui import QApplication, QHBoxLayout, QLabel

from qtlayoutbuilder.lib.widgetandlayoutfinder import WidgetAndLayoutFinder


class HasBox(object):
    """ The tests search for the QHBoxLayout inside instances of these. """

    def __init__(self):
        self.fibble = QHBoxLayout()


class HasLabel(object):
    """ The tests search for the QLabel inside instances of these. """

    def __init__(self):
        self.fibble = QLabel()


class TestWidgetAndLayoutFinder(TestCase):

    def setUp(self):
        super(TestWidgetAndLayoutFinder, self).setUp()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists

    # noinspection PyUnusedLocal
    def test_search_for_widget(self):

        # Make sure it discriminates on the particular class you specify,
        # and succeeds in finding the target object.

        # Both of the classes instantiated here have an attribute 'fibble' which
        # points to a QLayout or a QWidget, but only one should satisfy our
        # search because they embed different types of QObject.
        target_a = HasBox()
        target_b = HasLabel()

        finder = WidgetAndLayoutFinder()
        found = finder.find('QLabel', 'fibble')
        self.assertEquals(len(found), 1)
        found_object = found[0]
        self.assertEquals(found_object, target_b.fibble)
