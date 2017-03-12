from unittest import TestCase

from inputtextrecord import InputTextRecord
from inputsplitter import _FileLocation
from layouterror import LayoutError
import keywords

class TestInputTextRecord(TestCase):

    FILE_LOCATION = _FileLocation('dummy filename', 1)

    def test_get_segments_of_lhs_word(self):

        # Proper error handling if contains a space.
        try:
            InputTextRecord._get_segments_of_lhs_word(
                'HBOX: my_box', self.FILE_LOCATION)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue('Left hand side word: <HBOX: my_box>, must not contain whitespace,' in msg)

        # Proper error handling if splitting produces empty segment.
        try:
            InputTextRecord._get_segments_of_lhs_word(
                'HBOX:', self.FILE_LOCATION)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'One of the segments produced by splitting this word: <HBOX:> using colons is empty,' in msg)

        # Proper error handling when splitting on colons produces
        # too few segments.
        try:
            InputTextRecord._get_segments_of_lhs_word(
                'aaaaa', self.FILE_LOCATION)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'Splitting this word: <aaaaa> using colons does not produce 2 or 3 segments as required.' in msg)

        # Proper error handling when splitting on colons produces
        # too many segments.
        try:
            InputTextRecord._get_segments_of_lhs_word(
                'HBOX:a:b:c', self.FILE_LOCATION)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'Splitting this word: <HBOX:a:b:c> using colons does not produce 2 or 3 segments as required.' in msg)


    def test_populate_from_lhs_word(self):

        # Sensible error when none of the expected forms
        # are present.
        record = InputTextRecord(self.FILE_LOCATION)
        try:
            record._populate_from_lhs_word('DUFF_KEYWORD:my_box')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'Cannot detect any of the allowed forms in ' in msg)
            self.assertTrue(
                'this left hand side: <DUFF_KEYWORD:my_box>' in msg)

        # Correctly recognizes keyword forms
        for keyword in keywords.WORDS:
            record = InputTextRecord(self.FILE_LOCATION)
            lhs = '%s:my_thing' % keyword
            record._populate_from_lhs_word(lhs)
            self.assertEquals(record.make_or_find, record.INSTANTIATE)
            self.assertEquals(record.class_required, keywords.class_required_for(keyword))
            self.assertEquals(record.parent_name, 'my_thing')

        # Correctly recognizes Find form
        record = InputTextRecord(self.FILE_LOCATION)
        lhs = 'Find:MyCustomClass:custom_a'
        record._populate_from_lhs_word(lhs)
        self.assertEquals(record.make_or_find, record.FIND)
        self.assertEquals(record.class_required, 'MyCustomClass')
        self.assertEquals(record.parent_name, 'custom_a')

        # Correctly recognizes QWord form
        record = InputTextRecord(self.FILE_LOCATION)
        lhs = 'QLabel:my_label'
        record._populate_from_lhs_word(lhs)
        self.assertEquals(record.make_or_find, record.INSTANTIATE)
        self.assertEquals(record.class_required, 'QLabel')
        self.assertEquals(record.parent_name, 'my_label')

    def test_make_from_lhs_word(self):
        lhs = 'QLabel:my_label'
        record = InputTextRecord.make_from_lhs_word(lhs, self.FILE_LOCATION)
        self.assertEquals(record.file_location, self.FILE_LOCATION)
        self.assertEquals(record.make_or_find, record.INSTANTIATE)
        self.assertEquals(record.class_required, 'QLabel')
        self.assertEquals(record.parent_name, 'my_label')
        self.assertEquals(len(record.child_names), 0)

    def test_make_from_all_words(self):
        words = ['QLabel:my_label', 'a', 'b']
        record = InputTextRecord.make_from_all_words(words, self.FILE_LOCATION)
        self.assertEquals(record.file_location, self.FILE_LOCATION)
        self.assertEquals(record.make_or_find, record.INSTANTIATE)
        self.assertEquals(record.class_required, 'QLabel')
        self.assertEquals(record.parent_name, 'my_label')
        self.assertEquals(len(record.child_names), 2)
        self.assertEquals(record.child_names[1], 'b')
