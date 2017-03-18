"""
This module provides unit tests for the parentmaker module.
"""
from unittest import TestCase
from PySide.QtGui import QLabel, QHBoxLayout, qApp, QApplication, QLayout

import os.path

from widgetandlayoutfinder import WidgetAndLayoutFinder
import qobjectmaker
from layouterror import LayoutError
from filelocation import FileLocation
from inputtextrecord import InputTextRecord


class TestQObjectMaker(TestCase):
    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestQObjectMaker, cls).setUpClass()
        if qApp is None:
            QApplication([])

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
            q_object, parent_name = qobjectmaker.make_from_record(
                record, widget_or_layout_finder)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("Python cannot make any sense of this word" in msg)
            self.assertTrue(
                "(it does not exist in the global namespace)" in msg)
            self.assertTrue("<QThisWillNotExist>" in msg)

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
            q_object, parent_name = qobjectmaker.make_from_record(
                record, widget_or_layout_finder)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("Cannot instantiate one of these: <__doc__>" in msg)
            self.assertTrue("It is supposed to be a QtQui class" in msg)
            self.assertTrue("like QString or" in msg)
            self.assertTrue("QLabel that can be used as a constructor." in msg)
            self.assertTrue("When the code tried to instantiate one..." in msg)
            self.assertTrue("the underlying error message was:" in msg)
            self.assertTrue("<'str' object is not callable>" in msg)

        # Suitable error when the thing gets instantiated, but turns out not to be
        # a QWidget or QLayout
        words = ['QColor:my_label', 'foo']
        record = InputTextRecord.make_from_all_words(
            words, self.DUMMY_FILE_LOC)
        try:
            widget_or_layout_finder = None
            q_object, parent_name = qobjectmaker.make_from_record(
                record, widget_or_layout_finder)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("This class name: <QColor>" in msg)
            self.assertTrue("instantiates successfully," in msg)
            self.assertTrue("but is neither a QLayout, nor a QWidget," in msg)

        # Works properly when the QWord is explicit.
        words = ['QLabel:my_label', 'foo']
        record = InputTextRecord.make_from_all_words \
            (words, self.DUMMY_FILE_LOC)
        widget_or_layout_finder = None
        q_object, parent_name = qobjectmaker.make_from_record(
            record, widget_or_layout_finder)
        class_name = q_object.__class__.__name__
        self.assertTrue(isinstance(q_object, QLabel))
        self.assertEquals(parent_name, 'my_label')

        # Works properly when the QWord is implicit (ie a keyword).
        words = ['HBOX:my_box', 'foo']
        record = InputTextRecord.make_from_all_words \
            (words, self.DUMMY_FILE_LOC)
        widget_or_layout_finder = None
        q_object, parent_name = qobjectmaker.make_from_record(
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
            q_object, parent_name = qobjectmaker.make_from_record(
                record, widget_or_layout_finder)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'Cannot find any objects of class: <CustomLayout>'
                in msg)
            self.assertTrue(
                'that are referenced by a variable called: <my_page>'
                in msg)

        # Correct error handling when duplicates found.
        words = ['Find:CustomLayout:my_page', 'a', 'b', 'c']
        record = InputTextRecord.make_from_all_words(
            words, self.DUMMY_FILE_LOC)
        has_target_object_in_a = HasTargetIn()
        has_target_object_in_b = HasTargetIn()
        widget_or_layout_finder = WidgetAndLayoutFinder()
        try:
            q_object, parent_name = qobjectmaker.make_from_record(
                record, widget_or_layout_finder)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'Ambiguity Problem: Found more than one objects of class: <CustomLayout>'
                in msg)
            self.assertTrue(
                'that is referenced by a variable called: <my_page>'
                in msg)

        # Finds the target QObject when it should.
        words = ['Find:CustomLayout:my_solitary_page', 'a', 'b', 'c']
        record = InputTextRecord.make_from_all_words(
            words, self.DUMMY_FILE_LOC)
        my_solitary_page = CustomLayout()
        widget_or_layout_finder = WidgetAndLayoutFinder()
        q_object, parent_name = qobjectmaker.make_from_record(
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
