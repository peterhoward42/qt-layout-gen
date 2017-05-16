"""
This module provides unit tests for the parentmaker module.
"""
from unittest import TestCase

from PySide.QtGui import QApplication, QSpacerItem
from PySide.QtGui import QHBoxLayout
from PySide.QtGui import QLayout

from qtlayoutbuilder.lib.qobjectmaker import QObjectMaker
from qtlayoutbuilder.lib.widgetandlayoutfinder import WidgetAndLayoutFinder
from qtlayoutbuilder.lib_test.test_utils import \
    raises_layout_error_with_this_message


class TestQObjectMaker(TestCase):
    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestQObjectMaker, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists

    # First the instantiation behaviour.

    # Use cases that should work.

    def test_explicit_qt_class_instantiation(self):
        finder = None
        maker = QObjectMaker(finder)
        object_made = maker.make('fred', 'QHBoxLayout')
        self.assertTrue(isinstance(object_made, QHBoxLayout))

    def test_special_cases_qt_class_instantiation(self):
        # QSpacerItem cannot be contstructed with no arguments, so the object
        # maker passes in 0,0 as width, height.
        finder = None
        maker = QObjectMaker(finder)
        object_made = maker.make('fred', 'QSpacerItem')
        self.assertTrue(isinstance(object_made, QSpacerItem))

    # Error handling.

    def test_unrecognized_class(self):
        # Specify the required class as HBoxLayout (omitting the Q)
        finder = None
        maker = QObjectMaker(finder)
        result = raises_layout_error_with_this_message("""
            Python cannot find this word in the QtGui namespace: <HBoxLayout>,
            Did you mean one of these:

            QHBoxLayout
            QBoxLayout
            QVBoxLayout
            QLayout
            QTextLayout
            QFormLayout
        """, maker.make, 'fred', 'HBoxLayout')
        if not result:
            self.fail()

    def test_cannot_instantiate(self):
        finder = None
        maker = QObjectMaker(finder)
        result = raises_layout_error_with_this_message("""
            Cannot instantiate one of these: <__name__>.
            It is supposed to be the name a a QLayout or QWidget
            class, that can be used as a constructor.
            The error coming back from Python is:
            'str' object is not callable.
        """, maker.make, 'fred', '__name__')
        if not result:
            self.fail()

    def test_not_a_layout_or_widget(self):
        finder = None
        maker = QObjectMaker(finder)
        result = raises_layout_error_with_this_message("""
            This class name: <QColor>, instantiates successfully,
            but is neither a QLayout nor a QWidget.
        """, maker.make, 'fred', 'QColor')
        if not result:
            self.fail()

    # Now the 'Finding' behaviour.

    # noinspection PyUnusedLocal
    def test_finding_should_work_without_error(self):
        my_page = CustomLayout()
        finder = WidgetAndLayoutFinder()
        maker = QObjectMaker(finder)
        made = maker.make('my_page', '?CustomLayout')
        self.assertTrue(isinstance(made, CustomLayout))

    def test_finding_error_handling_when_nothing_found(self):
        finder = WidgetAndLayoutFinder()
        maker = QObjectMaker(finder)
        result = raises_layout_error_with_this_message("""
            Cannot find any objects of class <CustomLayout>,
            that are referenced by a variable or attribute
            called <wont_find_me>
        """, maker.make, 'wont_find_me', '?CustomLayout')
        if not result:
            self.fail()

    # noinspection PyUnusedLocal
    def test_finding_error_handling_when_duplicates_found(self):
        # Create two items that should get found and thus be duplicates.
        # Assign them the local variables to defeat immediate GC.
        my_page = CustomLayout()
        arbitrary = HasTargetIn()

        finder = WidgetAndLayoutFinder()
        maker = QObjectMaker(finder)
        result = raises_layout_error_with_this_message("""
            Ambiguity problem. Found more than one object of
            class: <CustomLayout>, referenced by a variable or attribute
            called: <my_page>
        """, maker.make, 'my_page', '?CustomLayout')
        if not result:
            self.fail()


class CustomLayout(QLayout):
    # A custom QLayout-derived class we can search for instances of.
    pass


class HasTargetIn(object):
    # A thing we can instantiate that has a member attribute, of our custom
    # QLayout class, pointed to by our target attribute name.
    def __init__(self):
        self.my_page = CustomLayout()
