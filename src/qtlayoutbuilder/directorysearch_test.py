from unittest import TestCase

import os.path

from directorysearch import DirectorySearch

_TOP_LEVEL_DIR = os.path.abspath(os.path.join(__file__, "../../..", 'testdata', 'simple_hierarchy'))
_EMPTY_DIR = os.path.abspath(os.path.join(__file__, "../../..", 'testdata', 'simple_hierarchy',
                                          'dir_in_top_level', 'dir_in_second_level'))
_NO_SUCH_DIR = 'ridiculousdirname'


class TestDirectorySearch(TestCase):
    """
    We use a very small, rigged, directory hierarchy as our test data.
    """

    def test_finds_all_files_expected(self):
        files, err = DirectorySearch.find_all_files(_TOP_LEVEL_DIR)
        self.assertIsNone(err)
        file_names_alone = [os.path.basename(f) for f in files]
        files_formatted = str(file_names_alone)
        self.assertEquals(files_formatted, "['top_level_a.txt', 'top_level_b.txt', 'second_level_a.txt']")

    def test_treats_empty_result_as_error(self):
        files, err = DirectorySearch.find_all_files(_EMPTY_DIR)
        self.assertIsNone(files)
        self.assertIsNotNone(err)
        message = err.format_as_single_string()
        self.assertTrue(message.startswith('Error stack:\n\n1: No files found'),
                        'Message: <%s>, does not start as it should' % message)
        self.assertTrue('dir_in_second_level' in message, 'Message: <%s>, does not cite directory properly' % message)

    def test_reports_os_level_error_properly(self):
        files, err = DirectorySearch.find_all_files(_NO_SUCH_DIR)
        self.assertIsNone(files)
        self.assertIsNotNone(err)
        message = err.format_as_single_string()
        self.assertTrue(message.startswith('Error stack:\n\n1: Something went wrong'),
                        'Message: <%s>, does not start as it should' % message)
        self.assertTrue('ridiculous' in message, 'Message: <%s>, does not cite directory properly' % message)
        self.assertTrue('The system cannot find the path specified' in message,
                        'Message: <%s>, does not cite underlying system error' % message)
