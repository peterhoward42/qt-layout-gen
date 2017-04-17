from unittest import TestCase

from qtlayoutbuilder.lib.multiline_string_utils import MultilineString
from qtlayoutbuilder.lib.original_file_rewriter import OriginalFileReWriter


class TestOriginalFileReWriter(TestCase):

    # Lower level functions first.

    def test_add_backup_location_comment(self):
        # First check that we get what we expect when the existing
        # one_big_string, does not already have such a comment in.

        one_big_string = 'just this text'
        mock_backup_folder_string = 'mock_backup_folder'
        output = OriginalFileReWriter._add_backup_location_comment(
                mock_backup_folder_string, one_big_string)
        output = MultilineString.normalise(output)
        expected = MultilineString.normalise("""
            # This file has been automatically re-formatted.
            # Previous versions can be found here:
            # mock_backup_folder
            ##
            just this text
        """)
        self.assertEquals(output, expected)

        # Now ensure that if we do it again - but this time with the
        # new one_big_string that already has a comment in, the old comment
        # gets replaced with the new.
        previous_output = output
        mock_backup_folder_string = 'DIFFERENT_mock_backup_folder'
        new_output = \
            OriginalFileReWriter._add_backup_location_comment(
                mock_backup_folder_string, previous_output)
        new_output = MultilineString.normalise(new_output)
        expected = MultilineString.normalise("""
            # This file has been automatically re-formatted.
            # Previous versions can be found here:
            # DIFFERENT_mock_backup_folder
            ##
            just this text
        """)
        self.assertEquals(new_output, expected)

