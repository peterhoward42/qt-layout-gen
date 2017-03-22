import os.path
from tempfile import mkdtemp
from unittest import TestCase

from qtlayoutbuilder.lib.directorysearch import find_all_files
from qtlayoutbuilder.api.layouterror import LayoutError

_TOP_LEVEL_DIR = os.path.abspath(
    os.path.join(__file__,
                 "../../../..",
                 'testdata',
                 'simple_hierarchy'))

_NO_SUCH_DIR = 'ridiculousdirname'

class TestDirectorySearch(TestCase):
    """
    We use a very small, rigged, directory hierarchy as our lib_test data.
    """

    def setUp(self):
        self.empty_directory = mkdtemp()

    def tearDown(self):
        os.rmdir(self.empty_directory)

    def test_reports_os_level_error_properly(self):
        try:
            find_all_files(_NO_SUCH_DIR)
        except LayoutError as e:
            self.assertTrue(
                r"The system cannot find the path specified: 'ridiculousdirname/*.*'" in str(e))

    def test_treats_empty_result_as_error(self):
        try:
            find_all_files(self.empty_directory)
        except LayoutError as e:
            self.assertTrue('No files found in' in str(e))
            self.assertTrue('temp' in str(e))

    def test_finds_all_files_expected(self):
        files = find_all_files(_TOP_LEVEL_DIR)
        file_names_alone = [os.path.basename(f) for f in files]
        files_formatted = str(file_names_alone)
        self.assertEquals(files_formatted,
                          "['top_level_a.txt', 'top_level_b.txt', 'second_level_a.txt']")
