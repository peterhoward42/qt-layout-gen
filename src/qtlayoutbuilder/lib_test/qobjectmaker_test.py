"""
This module provides unit tests for the parentmaker module.
"""
from unittest import TestCase

from PySide.QtGui import QLabel, QHBoxLayout, qApp, QApplication, QLayout

from qtlayoutbuilder.api.filelocation import FileLocation
from qtlayoutbuilder.api.layouterror import LayoutError

from qtlayoutbuilder.lib import qobjectmaker
from qtlayoutbuilder.lib.inputtextrecord import InputTextRecord
from qtlayoutbuilder.lib.widgetandlayoutfinder import WidgetAndLayoutFinder
from qtlayoutbuilder.test_utils import test_utils


class TestQObjectMaker(TestCase):
    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestQObjectMaker, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass # Singleton already exists

    DUMMY_FILE_LOC = FileLocation('pretend filename', 1)

    def test_the_instantiation_behaviour(self):
        # Prove out the operation of the syntax variants that require a new
        # widget or layout to be instantiated:
        #   'QHBoxLayout:my_box a b c'.
        #   'HBOX:my_box a b c'.

        # Suitable error when the class type is not recognized by python.
        words = ['QThisWillNotExist:my_label', 'foo']
        record = InputTextRecord.make_from_all_words(
            words, self.DUMMY_FILE_LOC)
        widget_or_layout_finder = None
        try:
            q_object, parent_name = qobjectmaker.make_from_parent_info(
                record, widget_or_layout_finder)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               Python cannot make any sense of this word. (it does not
               exist in the global namespace) <QThisWillNotExist>,
            """, msg))

        # Suitable error when python recognizes the word in the global namespace,
        # but cannot instantiate it.
        # We use the string __doc__ because we know that Python will be
        # able to resolve that name in the namespace the called function has,
        # but it is not instantiable, because it is a string and a string is not
        # a callable.

        # We have to monkey-patch the record to defeat the parser's
        # insistence that the word used for a QObject class begins with a Q.
        # So we start with QLabel...
        words = ['QLabel:my_label', 'foo']
        record = InputTextRecord.make_from_all_words(
            words, self.DUMMY_FILE_LOC)
        # Then overwrite the class name inside the record.
        record.class_required = '__doc__'
        try:
            widget_or_layout_finder = None
            q_object, parent_name = qobjectmaker.make_from_parent_info(
                record, widget_or_layout_finder)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                Cannot instantiate one of these: <__doc__>.
                It is supposed to be a QtQui class name like QString or
                QLabel that can be used as a constructor.
                When the code tried to instantiate one...
                the underlying error message was: <'str' object is not callable>,
            """, msg))

        # Suitable error when the thing gets instantiated, but turns out not to be
        # a QWidget or QLayout
        words = ['QColor:my_label', 'foo']
        record = InputTextRecord.make_from_all_words(
            words, self.DUMMY_FILE_LOC)
        try:
            widget_or_layout_finder = None
            q_object, parent_name = qobjectmaker.make_from_parent_info(
                record, widget_or_layout_finder)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               This class name: <QColor> instantiates successfully,
                but is neither a QLayout, nor a QWidget,
            """, msg))

        # Works properly when the QWord is explicit.
        words = ['QLabel:my_label', 'foo']
        record = InputTextRecord.make_from_all_words \
            (words, self.DUMMY_FILE_LOC)
        widget_or_layout_finder = None
        q_object, parent_name = qobjectmaker.make_from_parent_info(
            record, widget_or_layout_finder)
        class_name = q_object.__class__.__name__
        self.assertTrue(isinstance(q_object, QLabel))
        self.assertEquals(parent_name, 'my_label')

        # Works properly when the QWord is implicit (ie a keyword).
        words = ['HBOX:my_box', 'foo']
        record = InputTextRecord.make_from_all_words \
            (words, self.DUMMY_FILE_LOC)
        widget_or_layout_finder = None
        q_object, parent_name = qobjectmaker.make_from_parent_info(
            record, widget_or_layout_finder)
        class_name = q_object.__class__.__name__
        self.assertTrue(isinstance(q_object, QHBoxLayout))
        self.assertEquals(parent_name, 'my_box')

    def test_the_finding_behaviour(self):
        # Prove out the operation of the syntax variant that requires an
        # existing layout or widget to be found:
        #   'Find:CustomLayout:my_page a b c'.

        # Correct error handling when nothing found.
        words = ['Find:CustomLayout:my_page', 'a', 'b', 'c']
        record = InputTextRecord.make_from_all_words(
            words, self.DUMMY_FILE_LOC)
        widget_or_layout_finder = WidgetAndLayoutFinder()
        try:
            q_object, parent_name = qobjectmaker.make_from_parent_info(
                record, widget_or_layout_finder)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                Cannot find any objects of class: <CustomLayout>,
                that are referenced by a variable called: <my_page>.
            """, msg))

        # Correct error handling when duplicates found.
        words = ['Find:CustomLayout:my_page', 'a', 'b', 'c']
        record = InputTextRecord.make_from_all_words(
            words, self.DUMMY_FILE_LOC)
        has_target_object_in_a = HasTargetIn()
        has_target_object_in_b = HasTargetIn()
        widget_or_layout_finder = WidgetAndLayoutFinder()
        try:
            q_object, parent_name = qobjectmaker.make_from_parent_info(
                record, widget_or_layout_finder)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               Ambiguity Problem: Found more than one objects of class:
               <CustomLayout>,
               that is referenced by a variable called: <my_page>.
            """, msg))

        # Finds the target QObject when it should.
        words = ['Find:CustomLayout:my_solitary_page', 'a', 'b', 'c']
        record = InputTextRecord.make_from_all_words(
            words, self.DUMMY_FILE_LOC)
        my_solitary_page = CustomLayout()
        widget_or_layout_finder = WidgetAndLayoutFinder()
        q_object, parent_name = qobjectmaker.make_from_parent_info(
            record, widget_or_layout_finder)
        self.assertEquals(parent_name, 'my_solitary_page')
        self.assertEquals(q_object.__class__.__name__, 'CustomLayout')


class CustomLayout(QLayout):
    # A custom QLayout-derived class we can search for instances of.
    pass


class HasTargetIn(object):
    # A thing we can instantiate that has a member attribute, of our custom
    # QLayout class, pointed to by our target attribute name.
    def __init__(self):
        self.my_page = CustomLayout()
