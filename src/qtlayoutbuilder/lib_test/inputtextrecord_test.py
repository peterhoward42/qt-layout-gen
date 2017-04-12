from unittest import TestCase

from qtlayoutbuilder.api.layouterror import LayoutError

import qtlayoutbuilder.lib.keywords
from qtlayoutbuilder.lib.inputtextrecord import InputTextRecord
from qtlayoutbuilder.lib_test import test_utils


class TestInputTextRecord(TestCase):
    def test_get_segments_of_lhs_word(self):

        # Proper error handling if contains a space.
        try:
            InputTextRecord._get_segments_of_lhs_word('my_box: HBOX',
                    InputTextRecord.mock_file_location())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               Left hand side word: <my_box: HBOX>, must
               not contain whitespace,
            """, msg))

        # Proper error handling if splitting produces empty segment.
        try:
            InputTextRecord._get_segments_of_lhs_word('my_label:',
                    InputTextRecord.mock_file_location())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               One of the segments produced by splitting this word:
               <my_label:> using colons is empty,
            """, msg))

        # Proper error handling when splitting on colons produces
        # too few segments.
        try:
            InputTextRecord._get_segments_of_lhs_word('aaaaa',
                    InputTextRecord.mock_file_location())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               Splitting this word: <aaaaa> using colons does not produce
               2 or 3 segments as required.
            """, msg))

        # Proper error handling when splitting on colons produces
        # too many segments.
        try:
            InputTextRecord._get_segments_of_lhs_word('a:b:c:d:e',
                    InputTextRecord.mock_file_location())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               Splitting this word: <a:b:c:d:e> using colons does not produce
               2 or 3 segments as required.
            """, msg))

    def test_populate_from_lhs_word(self):

        # Sensible error when none of the expected forms
        # are present.
        record = InputTextRecord(InputTextRecord.mock_file_location())
        try:
            record._populate_from_lhs_word('my_box:DUFF_KEYWORD')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               Cannot detect any of the allowed forms in this left hand
               side: <my_box:DUFF_KEYWORD>,
            """, msg))

        # Correctly recognizes keyword forms
        for keyword in qtlayoutbuilder.lib.keywords.WORDS:
            record = InputTextRecord(InputTextRecord.mock_file_location())
            lhs = 'my_thing:%s' % keyword
            record._populate_from_lhs_word(lhs)
            self.assertEquals(record.make_or_find, record.INSTANTIATE)
            self.assertEquals(record.class_required,
                    qtlayoutbuilder.lib.keywords.class_required_for(keyword))
            self.assertEquals(record.parent_name, 'my_thing')

        # Correctly recognizes Find form
        record = InputTextRecord(InputTextRecord.mock_file_location())
        lhs = 'custom_a:Find:MyCustomClass'
        record._populate_from_lhs_word(lhs)
        self.assertEquals(record.make_or_find, record.FIND)
        self.assertEquals(record.class_required, 'MyCustomClass')
        self.assertEquals(record.parent_name, 'custom_a')

        # Correctly recognizes QWord form
        record = InputTextRecord(InputTextRecord.mock_file_location())
        lhs = 'my_label:QLabel'
        record._populate_from_lhs_word(lhs)
        self.assertEquals(record.make_or_find, record.INSTANTIATE)
        self.assertEquals(record.class_required, 'QLabel')
        self.assertEquals(record.parent_name, 'my_label')

    def test_make_from_lhs_word(self):
        lhs = 'my_label:QLabel'
        record = InputTextRecord.make_from_lhs_word(lhs,
                InputTextRecord.mock_file_location())
        self.assertEquals(record.file_location,
                InputTextRecord.mock_file_location())
        self.assertEquals(record.make_or_find, record.INSTANTIATE)
        self.assertEquals(record.class_required, 'QLabel')
        self.assertEquals(record.parent_name, 'my_label')
        self.assertEquals(len(record.child_names), 0)

    def test_make_from_all_words(self):
        words = ['my_label:QLabel', 'a', 'b']
        record = InputTextRecord.make_from_all_words(words,
                InputTextRecord.mock_file_location())
        self.assertEquals(record.file_location,
                InputTextRecord.mock_file_location())
        self.assertEquals(record.make_or_find, record.INSTANTIATE)
        self.assertEquals(record.class_required, 'QLabel')
        self.assertEquals(record.parent_name, 'my_label')
        self.assertEquals(len(record.child_names), 2)
        self.assertEquals(record.child_names[1], 'b')
