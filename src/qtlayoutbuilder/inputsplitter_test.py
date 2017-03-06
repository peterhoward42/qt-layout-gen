from unittest import TestCase

import os.path

# noinspection PyProtectedMember
from inputsplitter import _check_validity_of_name, _check_name_list_from_record, _make_text_record_from_fragment, \
    _FileLocation, \
    _split_text_into_records, _cleaned_up, _split_file_into_records


class TestInputSplitter(TestCase):
    def test_name_validity_checker(self):
        # Sensible name passes
        err = _check_validity_of_name('label_1')
        self.assertIsNone(err)

        # Starts with a number fails
        err = _check_validity_of_name('42_label')
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Name: <42_label> is not a valid identifier' in msg)

        # Illegal character present fails
        err = _check_validity_of_name('label_1#')
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Name: <label_1#> is not a valid identifier' in msg)

    def test_names(self):
        # Raises no objections to legitimate input
        err = _check_name_list_from_record(['foo' 'bar'])
        self.assertIsNotNone(err)

        # Objects to fewer than two names in the list
        err = _check_name_list_from_record(['foo'])
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Expected at least two names' in msg)

        # Objects when one of the names is malformed
        err = _check_name_list_from_record(['foo', '9illegal', 'bar'])
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Problem with one of the names' in msg)
        self.assertTrue('Name: <9illegal> is not a valid identifier' in msg)

    def test_make_text_record_from_fragment(self):
        mock_file_location = _FileLocation('unused filename', -1)

        # Objects when no acceptable keyword is at the front
        record, err = _make_text_record_from_fragment('NOTKWD: fred jane barry', mock_file_location)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Cannot find keyword at beginning of this string: <NOTKWD: fred jane barry>' in msg)

        # Objects when a colon doesn't come next
        record, err = _make_text_record_from_fragment('HBOX fred jane barry', mock_file_location)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Expected colon (:) after keyword in this string: <HBOX fred jane barry>' in msg)

        # Invokes name checker on all names present in remainder

        record, err = _make_text_record_from_fragment('HBOX:illegal# jane barry', mock_file_location)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Name: <illegal#> is not a valid identifier' in msg)

        record, err = _make_text_record_from_fragment('HBOX:fred jane illegal#', mock_file_location)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Name: <illegal#> is not a valid identifier' in msg)

        # Harvests everything required into the returned input text record

        record, err = _make_text_record_from_fragment('HBOX:fred jane barry', mock_file_location)
        self.assertIsNone(err)
        self.assertIsNotNone(record)

        self.assertEqual(record.file_location, mock_file_location)
        self.assertEqual(record.layout_keyword, 'HBOX')
        self.assertEqual(record.parent_name, 'fred')
        self.assertEqual(str(record.child_name_fields), "['jane', 'barry']")

    def test_cleaned_up(self):
        # The space item should be removed, and the leading space on
        # the word 'bar' should be removed.
        cleaned = _cleaned_up(['foo', ' ', ' bar'])
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned[0], 'foo')
        self.assertEqual(cleaned[1], 'bar')

    def test_split_text_into_records(self):
        # Failed to find any keywords to split on.
        records, err = _split_text_into_records('ipsum doo dah')
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('ould not split this text: <ipsum doo dah>' in msg)
        self.assertTrue('Cannot find keyword at beginning of this string: <ipsum doo dah>' in msg)

        # Error if one of the fragments found is malformed
        records, err = _split_text_into_records('HBOX:a b c HBOX:a b illegal#')
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Could not split this text: <HBOX:a b c HBOX:a b illegal#>' in msg)
        self.assertTrue('Problem with names in this input text fragment: <HBOX:a b illegal#>, at this fi' in msg)
        self.assertTrue('Problem with one of the names' in msg)
        self.assertTrue('Name: <illegal#> is not a valid identifier' in msg)

        # Gets well formed set of records when works
        records, err = _split_text_into_records('HBOX:a b c HBOX:d e f')
        self.assertIsNone(err)
        self.assertIsNotNone(records)

        self.assertEqual(len(records), 2)

        # Prove that the records have been assembled in the right order and have
        # not overwritten each other.
        self.assertEqual(records[0].parent_name, 'a')
        self.assertEqual(records[1].parent_name, 'd')

    def test_split_file_into_records(self):
        # Reports IO errors properly.
        records, err = _split_file_into_records('sillyfilename')
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Cannot split the file <sillyfilename> into records' in msg)
        self.assertTrue("No such file or directory: 'sillyfilename'" in msg)

        # Objects to files that do not have a keyword on the first line properly
        malformed_file = os.path.abspath(
            os.path.join(
                __file__, "../../..", 'testdata', 'file_with_illegal_first_line.txt'))
        records, err = _split_file_into_records(malformed_file)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('The first line of your file must start with a keyword:' in msg)
        self.assertTrue('file_with_illegal_first_line.txt' in msg)

        # Bubbles error messages up from lower down with correct line number.
        malformed_file = os.path.abspath(
            os.path.join(
                __file__, "../../..", 'testdata', 'file_to_stimulate_parse_error.txt'))
        records, err = _split_file_into_records(malformed_file)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Problem with names in this input text fragment: <VBOX:my_vbox top body# right>' in msg)
        self.assertTrue('at this file location:' in msg)
        self.assertTrue('file_to_stimulate_parse_error.txt, at line 2' in msg)

        # Assembles records in correct order and with correct content for properly formed
        # input file.
        properly_formed_file = os.path.abspath(
            os.path.join(
                __file__, "../../..", 'testdata', 'properly_formed_file.txt'))
        records, err = _split_file_into_records(properly_formed_file)
        self.assertIsNone(err)
        self.assertIsNotNone(records)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].parent_name, 'my_hbox')
        self.assertEqual(records[1].parent_name, 'my_vbox')
