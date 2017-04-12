import os.path
from unittest import TestCase

from qtlayoutbuilder.api.layouterror import LayoutError

from qtlayoutbuilder.lib.inputsplitter import _remove_comments_from_line, \
    split_big_string_into_records, \
    split_all_files_in_directory_into_records, split_file_into_records
from qtlayoutbuilder.lib_test import test_utils


class TestInputSplitter(TestCase):

    def test_utilities(self):
        # Basic
        result = _remove_comments_from_line('foo#bar')
        self.assertEquals(result, 'foo')

        # No-op
        result = _remove_comments_from_line('foobarbaz')
        self.assertEquals(result, 'foobarbaz')

    def test_split_file_into_records(self):
        # Reports IO errors properly.
        try:
            records = split_file_into_records('sillyfilename')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               [Errno 2] No such file or directory: 'sillyfilename',
            """, msg))

        # Raises an error if the first word in the file is not
        # a colon-word
        malformed_file = os.path.abspath(
            os.path.join(
                __file__,
                "../../../..",
                'testdata',
                'file_with_illegal_first_word.txt'))

        try:
            records = split_file_into_records(malformed_file)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               The first word of your input must have a colon in it:
            """, msg))

        # Raises an error if no records found
        malformed_file = os.path.abspath(
            os.path.join(
                __file__,
                "../../../..",
                'testdata',
                'file_with_nothing_in.txt'))
        try:
            records = split_file_into_records(malformed_file)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               Nothing found in this file:
            """, msg))

        # Harvests correct records when input is properly formed.
        # (The input file includes comments)
        properly_formed_file = os.path.abspath(
            os.path.join(
                __file__,
                "../../../..",
                'testdata',
                'simple_hierarchy',
                'top_level_a.txt'))

        records = split_file_into_records(properly_formed_file)
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
            records = split_big_string_into_records('ipsum doo dah')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               The first word of your input must have a colon in it:
            """, msg))

        # Raises error when two children of the same name cited in the record
        try:
            records = split_big_string_into_records('foo:HBOX a a')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               Cannot specify two children of the same name.
            """, msg))

        # But tolerates two usages of '<>' as child names in same record.
        records = split_big_string_into_records('foo:HBOX <> a <>')
        self.assertIsNotNone(records)

        # Harvests correct words when input is properly formed
        records = split_big_string_into_records('a:HBOX b c d:HBOX e f')
        self.assertIsNotNone(records)
        self.assertEqual(len(records), 2)
        # We need only test the record aggregation, not the
        # parsing of each one.
        self.assertEqual(records[0].parent_name, 'a')
        self.assertEqual(records[1].parent_name, 'd')

        # Harvests correct words when comments are present.
        records = split_big_string_into_records("""

                my_box:HBOX left right

                # explain something

                left:QLabel hello
                right:QLabel fred
            """)
        self.assertIsNotNone(records)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0].parent_name, 'my_box')
        self.assertEqual(records[0].child_names, ['left', 'right'])
        self.assertEqual(records[1].parent_name, 'left')
        self.assertEqual(records[1].child_names, ['hello'] )
        self.assertEqual(records[2].parent_name, 'right')
        self.assertEqual(records[2].child_names, ['fred'])

    def test_split_all_files_in_directory_into_records(self):
        # Reports os level problems properly.
        try:
            records = split_all_files_in_directory_into_records('sillydirname')
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                r"The system cannot find the path specified: 'sillydirname/*.*'" in msg)

        # Reports problems part way through properly
        directory_with_a_problem_file_in = os.path.abspath(os.path.join(
                __file__, "../../../..", 'testdata', 'hierarchy_with_problem_inside'))
        try:
            records = split_all_files_in_directory_into_records(directory_with_a_problem_file_in)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
               The first word of your input must have a colon in it:
            """, msg))

        # Is aggregating the records from more than one file.
        # Reports problems part way through properly
        simple_hierarchy = os.path.abspath(os.path.join(
            __file__, "../../../..", 'testdata', 'simple_hierarchy'))
        records = split_all_files_in_directory_into_records(simple_hierarchy)
        self.assertEqual(len(records), 8)
        self.assertEqual(records[0].parent_name, 'my_page')
        self.assertEqual(records[7].parent_name, 'd')
