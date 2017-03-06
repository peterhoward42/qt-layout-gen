from unittest import TestCase

# noinspection PyProtectedMember
from inputsplitter import _check_validity_of_name, _check_names, _make_text_record_from_fragment, _FileLocation


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
        err = _check_names(['foo' 'bar'])
        self.assertIsNotNone(err)

        # Objects to fewer than two names in the list
        err = _check_names(['foo'])
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Expected at least two names' in msg)

        # Objects when one of the names is malformed
        err = _check_names(['foo', '9illegal', 'bar'])
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('1: Problem with one of the names' in msg)
        self.assertTrue('2: Name: <9illegal> is not a valid identifier' in msg)

    def test_make_text_record_from_fragment(self):
        mock_file_location = _FileLocation('unused filename', -1)

        # Objects when no acceptable keyword is at the front
        record, err = _make_text_record_from_fragment('NOTKWD: fred jane barry', mock_file_location)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Cannot find keyword at beginning of this string: NOTKWD: fred jane barry' in msg)

        # Objects when a colon doesn't come next
        record, err = _make_text_record_from_fragment('HBOX fred jane barry', mock_file_location)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Expected colon (:) after keyword in this string: HBOX fred jane barry' in msg)

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
