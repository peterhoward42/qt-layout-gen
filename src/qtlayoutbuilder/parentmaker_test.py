"""
This module provides unit tests for the parentmaker module.
"""
from unittest import TestCase
from PySide.QtGui import QLabel

import os.path

# noinspection PyProtectedMember
from parentmaker import _deduce_lhs_producer_function, _make_qtype
from layouterror import LayoutError
from inputsplitter import _InputTextRecord, _FileLocation
import keywords


class TestParentMaker(TestCase):

    DUMMY_FILE_LOC = _FileLocation('pretend filename', 1)

    def test_deduce_lhs_producer_function(self):
        # The _deduce_lhs_producer_function takes a look at the
        # the LHS of an InputTextRecord, and works out which of constructor
        # it is asking for. It returns a factory function.

        # Check the error reporting when the LHS is malformed.
        # Instead of something like "HBOX:my_box fred", we provide garbage.
        try:
            words = ['banana', 'apple']
            fn = _deduce_lhs_producer_function(_InputTextRecord(self.DUMMY_FILE_LOC, words))
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("The left hand side: <banana> of your record" in msg)
            self.assertTrue("does not conform to any of the legal forms" in msg)
            self.assertTrue("(pretend filename, at line 1)" in msg)

        # Check that each syntactical variant is recognized properly.
        # Feed it all the legal keywords (like HBOX) and make sure it
        # chooses the make_keyword producer function.
        for keyword in keywords.WORDS:
            record = _InputTextRecord(self.DUMMY_FILE_LOC, ['%s:some_name' % keyword, 'foo'])
            fn_returned = _deduce_lhs_producer_function(record)
            produce_fn_as_string = str(fn_returned)
            self.assertTrue('function _make_keyword_type' in produce_fn_as_string)

    def test_make_qtype(self):
        # Prove out the operation of this syntax variant 'HBOX:my_box a b c'.

        # First test the error handling when there is nothing after
        # the colon on the LHS.
        words = ['ipsum:', 'foo']
        record = _InputTextRecord(self.DUMMY_FILE_LOC, words)
        try:
            q_object = _make_qtype(record)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("When we split this left hand side at the colon: <ipsum:>, we end up with one " in msg)
            self.assertTrue("that is of zero length" in msg)

        # Suitable error when the class type is not recognized by python.
        words = ['QThisWillNotExist:my_label', 'foo']
        record = _InputTextRecord(self.DUMMY_FILE_LOC, words)
        try:
            q_object = _make_qtype(record)
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
        words = ['__doc__:my_label', 'foo']
        record = _InputTextRecord(self.DUMMY_FILE_LOC, words)
        try:
            q_object = _make_qtype(record)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("Cannot instantiate one of these: <__doc__>" in msg)
            self.assertTrue("It is supposed to be a QtGui class name like QString or QLabel that can be used as a constructor." in msg)
            self.assertTrue("When the code tried to instantiate one." in msg)
            self.assertTrue("the underlying error message was: <'str' object is not callable>," in msg)

        # Suitable error when the thing gets instantiated, but turns out not to be
        # a QWidget or QLayout
        words = ['QColor:my_label', 'foo']
        record = _InputTextRecord(self.DUMMY_FILE_LOC, words)
        try:
            q_object = _make_qtype(record)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("This QWord: <QColor> instantiates, but is neither a QLayout or QWidget" in msg)

        # Works properly on well formed input
        words = ['QLabel:my_label', 'foo']
        record = _InputTextRecord(self.DUMMY_FILE_LOC, words)
        q_object = _make_qtype(record)
        class_name = q_object.__class__.__name__
        print class_name
        self.assertTrue(isinstance(q_object, QLabel))
