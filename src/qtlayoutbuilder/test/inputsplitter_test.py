import os.path
from unittest import TestCase

from qtlayoutbuilder.lib.filelocation import FileLocation
from qtlayoutbuilder.lib.inputsplitter import _split_big_string_into_records, \
    _split_file_into_records, _split_all_files_in_directory_into_records
from qtlayoutbuilder.lib.layouterror import LayoutError


class TestInputSplitter(TestCase):

    FILE_LOCATION = FileLocation('dummy filename', 1)

    def test_split_file_into_records(self):
        # Reports IO errors properly.
        try:
            records = _split_file_into_records('sillyfilename')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("No such file or directory: 'sillyfilename'" in msg)

        # Raises an error if the first word in the file is not
        # a colon-word
        malformed_file = os.path.abspath(
            os.path.join(
                __file__,
                "../../..",
                'testdata',
                'file_with_illegal_first_word.txt'))

        try:
            records = _split_file_into_records(malformed_file)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("The first word in your file must have a colon in it:" in msg)
            self.assertTrue(r"testdata\file_with_illegal_first_word.txt" in msg)

        # Raises an error if no records found
        malformed_file = os.path.abspath(
            os.path.join(
                __file__,
                "../../..",
                'testdata',
                'file_with_nothing_in.txt'))
        try:
            records, err = _split_file_into_records(malformed_file)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue("Nothing found in this file:" in msg)
            self.assertTrue(r"testdata\file_with_nothing_in.txt" in msg)

        # Harvests correct records when input is properly formed
        properly_formed_file = os.path.abspath(
            os.path.join(
                __file__,
                "../../..",
                'testdata',
                'simple_hierarchy',
                'top_level_a.txt'))

        records = _split_file_into_records(properly_formed_file)
        self.assertIsNotNone(records)
        self.assertEqual(len(records), 4)
        # We need only test the record aggregation, not the
        # parsing of each one.
        self.assertEqual(records[0].parent_name, 'my_page')
        self.assertEqual(records[1].parent_name, 'header_row')
        self.assertEqual(records[2].parent_name, 'body')
        self.assertEqual(records[3].parent_name, 'custom_a')

    def test_split_text_into_records(self):
        # Raises error when first word is not a colon-word
        try:
            records = _split_big_string_into_records('ipsum doo dah')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                "Error: The first word in your text must have a colon in it: <ipsum doo dah>" in msg)

        # Harvests correct words when input is properly formed
        records = _split_big_string_into_records('HBOX:a b c HBOX:d e f')
        self.assertIsNotNone(records)
        self.assertEqual(len(records), 2)
        # We need only test the record aggregation, not the
        # parsing of each one.
        self.assertEqual(records[0].parent_name, 'a')
        self.assertEqual(records[1].parent_name, 'd')

    def test_split_all_files_in_directory_into_records(self):
        # Reports os level problems properly.
        try:
            records = _split_all_files_in_directory_into_records('sillydirname')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                r"The system cannot find the path specified: 'sillydirname/*.*'" in msg)

        # Reports problems part way through properly
        directory_with_a_problem_file_in = os.path.abspath(os.path.join(
                __file__, "../../..", 'testdata', 'hierarchy_with_problem_inside'))
        try:
            records = _split_all_files_in_directory_into_records(directory_with_a_problem_file_in)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                "The first word in your file must have a colon in it" in msg)
            self.assertTrue(
                r"hierarchy_with_problem_inside\top_level_b.txt" in msg)

        # Is aggregating the records from more than one file.
        # Reports problems part way through properly
        simple_hierarchy = os.path.abspath(os.path.join(
            __file__, "../../..", 'testdata', 'simple_hierarchy'))
        records = _split_all_files_in_directory_into_records(simple_hierarchy)
        self.assertEqual(len(records), 8)
        self.assertEqual(records[0].parent_name, 'my_page')
        self.assertEqual(records[7].parent_name, 'd')
