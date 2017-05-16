import tempfile
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

    def test_make_backup_of_existing_file(self):
        # Make a file that we will then back up.
        orig_fd = tempfile.NamedTemporaryFile(delete=False)
        orig_file_path = orig_fd.name
        orig_fd.write('original file content')
        orig_fd.close()

        # Back it up
        backup_folder, backup_file_path = \
            OriginalFileReWriter._make_backup_of_existing_file(orig_file_path)

        # Ensure that the backed up file  has the expected content.
        with open(backup_file_path, 'r') as read_fd:
            content = read_fd.read()
            self.assertEqual(content, 'original file content')

    # Now at API level

    def test_at_api_level(self):
        # Make a file that we will then overwrite.
        orig_fd = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        orig_file_path = orig_fd.name
        content = MultilineString.shift_left("""
            layout      QHBoxLayout
              widget    QWidget
        """)
        orig_fd.write(content)
        orig_fd.close()

        # Mandate the overwrite
        OriginalFileReWriter.overwrite_original(orig_file_path, 'new content')

        # Check for both the presence of the new content, and the
        # backup message.
        with open(orig_file_path, 'r') as input_file:
            content = input_file.read()
            self.assertTrue('new content' in content)
            self.assertTrue('has been' in content)
