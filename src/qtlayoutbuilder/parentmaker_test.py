"""
This module provides unit tests for the parentmaker module.
"""
from unittest import TestCase
from PySide.QtGui import QLabel

import os.path

# noinspection PyProtectedMember
from parentmaker import make
from layouterror import LayoutError
from filelocation import FileLocation
from inputtextrecord import InputTextRecord


class TestParentMaker(TestCase):

    DUMMY_FILE_LOC = FileLocation('pretend filename', 1)

    def test_instantiate_q_object(self):
        # Prove out the operation of this syntax variant 'HBOX:my_box a b c'.

        # Suitable error when the class type is not recognized by python.
        words = ['QThisWillNotExist:my_label', 'foo']
        record = InputTextRecord.make_from_all_words(words, self.DUMMY_FILE_LOC)
        try:
            q_object = make(record)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("Python can't make any sense of this word." in msg)
            self.assertTrue("(it doesn't exist in the global namespace)" in msg)
            self.assertTrue("QThisWillNotExist" in msg)

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
        record = InputTextRecord.make_from_all_words(words, self.DUMMY_FILE_LOC)
        # Then overwrite the class name inside the record.
        record.class_required = '__doc__'
        try:
            q_object = make(record)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("Cannot instantiate one of these: <__doc__>" in msg)
            self.assertTrue("It is supposed to be a QtGui class name like QString or QLabel that can be used as a constructor." in msg)
            self.assertTrue("When the code tried to instantiate one." in msg)
            self.assertTrue("the underlying error message was: <'str' object is not callable>," in msg)

        # Suitable error when the thing gets instantiated, but turns out not to be
        # a QWidget or QLayout
        words = ['QColor:my_label', 'foo']
        record = InputTextRecord.make_from_all_words(words, self.DUMMY_FILE_LOC)
        try:
            q_object = make(record)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                "This class name: <QColor> instantiates successfully, but is neither a QLayout nor a QWidget" in msg)
        # We have to monkey-patch the record to defeat the parser's
        # insistence that the word used for a QObject class begins with a Q.

        # Works properly on well formed input
        words = ['QLabel:my_label', 'foo']
        record = InputTextRecord.make_from_all_words(words, self.DUMMY_FILE_LOC)
        q_object = make(record)
        class_name = q_object.__class__.__name__
        self.assertTrue(isinstance(q_object, QLabel))
