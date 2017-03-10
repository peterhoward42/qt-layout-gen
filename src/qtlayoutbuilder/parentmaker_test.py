from unittest import TestCase

import os.path

# noinspection PyProtectedMember
from parentmaker import _deduce_lhs_producer_function
from layouterror import LayoutError
from inputsplitter import _InputTextRecord, _FileLocation
import keywords


class TestParentMaker(TestCase):

    DUMMY_FILE_LOC = _FileLocation('pretend filename', 1)

    def test_deduce_lhs_producer_function(self):
        # Gives sensible error when the input is malformed.
        try:
            words = ['banana', 'apple']
            fn = _deduce_lhs_producer_function(_InputTextRecord(self.DUMMY_FILE_LOC, words))
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("The left hand side: <banana> of your record" in msg)
            self.assertTrue("does not conform to any of the legal forms" in msg)
            self.assertTrue("(pretend filename, at line 1)" in msg)

        # Can spot the keyword format
        for keyword in keywords.WORDS:
            record = _InputTextRecord(self.DUMMY_FILE_LOC, [keyword, 'foo'])
            fn_returned = _deduce_lhs_producer_function(record)
            produce_fn_as_string = str(fn_returned)
            self.assertTrue('function _make_keyword_type' in produce_fn_as_string)