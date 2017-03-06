from unittest import TestCase

from inputsplitter import _check_validity_of_name

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

        # Illegal character in middle fails
        err = _check_validity_of_name('has a space in')
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Name: <has a space in> is not a valid identifier' in msg)