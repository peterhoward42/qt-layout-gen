from unittest import TestCase

import qtlayoutbuilder.lib.keywords
from qtlayoutbuilder.api.filelocation import FileLocation
from qtlayoutbuilder.lib.inputtextrecord import InputTextRecord
from qtlayoutbuilder.api.layouterror import LayoutError


class TestInputTextRecord(TestCase):
    def test_get_segments_of_lhs_word(self):

        # Proper error handling if contains a space.
        try:
            InputTextRecord._get_segments_of_lhs_word('HBOX: my_box',
                    InputTextRecord.mock_file_location())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                    'Left hand side word: <HBOX: my_box>, must not contain '
                    'whitespace,' in msg)

        # Proper error handling if splitting produces empty segment.
        try:
            InputTextRecord._get_segments_of_lhs_word('HBOX:',
                    InputTextRecord.mock_file_location())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                    'One of the segments produced by splitting this word: '
                    '<HBOX:> '
                    'using colons is empty,' in msg)

        # Proper error handling when splitting on colons produces
        # too few segments.
        try:
            InputTextRecord._get_segments_of_lhs_word('aaaaa',
                    InputTextRecord.mock_file_location())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                    'Splitting this word: <aaaaa> using colons does not '
                    'produce 2 '
                    'or 3 segments as required.' in msg)

        # Proper error handling when splitting on colons produces
        # too many segments.
        try:
            InputTextRecord._get_segments_of_lhs_word('HBOX:a:b:c',
                    InputTextRecord.mock_file_location())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                    'Splitting this word: <HBOX:a:b:c> using colons does not '
                    'produce 2 or 3 segments as required.' in msg)

    def test_populate_from_lhs_word(self):

        # Sensible error when none of the expected forms
        # are present.
        record = InputTextRecord(InputTextRecord.mock_file_location())
        try:
            record._populate_from_lhs_word('DUFF_KEYWORD:my_box')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue('Cannot detect any of the allowed forms in ' in msg)
            self.assertTrue('this left hand side: <DUFF_KEYWORD:my_box>' in msg)

        # Correctly recognizes keyword forms
        for keyword in qtlayoutbuilder.lib.keywords.WORDS:
            record = InputTextRecord(InputTextRecord.mock_file_location())
            lhs = '%s:my_thing' % keyword
            record._populate_from_lhs_word(lhs)
            self.assertEquals(record.make_or_find, record.INSTANTIATE)
            self.assertEquals(record.class_required,
                    qtlayoutbuilder.lib.keywords.class_required_for(keyword))
            self.assertEquals(record.parent_name, 'my_thing')

        # Correctly recognizes Find form
        record = InputTextRecord(InputTextRecord.mock_file_location())
        lhs = 'Find:MyCustomClass:custom_a'
        record._populate_from_lhs_word(lhs)
        self.assertEquals(record.make_or_find, record.FIND)
        self.assertEquals(record.class_required, 'MyCustomClass')
        self.assertEquals(record.parent_name, 'custom_a')

        # Correctly recognizes QWord form
        record = InputTextRecord(InputTextRecord.mock_file_location())
        lhs = 'QLabel:my_label'
        record._populate_from_lhs_word(lhs)
        self.assertEquals(record.make_or_find, record.INSTANTIATE)
        self.assertEquals(record.class_required, 'QLabel')
        self.assertEquals(record.parent_name, 'my_label')

    def test_make_from_lhs_word(self):
        lhs = 'QLabel:my_label'
        record = InputTextRecord.make_from_lhs_word(lhs,
                InputTextRecord.mock_file_location())
        self.assertEquals(record.file_location,
                InputTextRecord.mock_file_location())
        self.assertEquals(record.make_or_find, record.INSTANTIATE)
        self.assertEquals(record.class_required, 'QLabel')
        self.assertEquals(record.parent_name, 'my_label')
        self.assertEquals(len(record.child_names), 0)

    def test_make_from_all_words(self):
        words = ['QLabel:my_label', 'a', 'b']
        record = InputTextRecord.make_from_all_words(words,
                InputTextRecord.mock_file_location())
        self.assertEquals(record.file_location,
                InputTextRecord.mock_file_location())
        self.assertEquals(record.make_or_find, record.INSTANTIATE)
        self.assertEquals(record.class_required, 'QLabel')
        self.assertEquals(record.parent_name, 'my_label')
        self.assertEquals(len(record.child_names), 2)
        self.assertEquals(record.child_names[1], 'b')
