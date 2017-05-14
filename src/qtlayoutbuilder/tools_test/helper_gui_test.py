import os
import shutil
import tempfile
from unittest import TestCase

from PySide.QtCore import QTimer
from PySide.QtGui import QApplication, qApp

from qtlayoutbuilder.lib.multiline_string_utils import MultilineString
from qtlayoutbuilder.tools.helper_gui import HelperGui


class TestHelperGui(TestCase):
    """
    Regression and portability tests for tools/helper_gui.py
    """

    _SIMPLE = 'simple.txt'

    _input_file_content = {}

    _input_file_content[_SIMPLE] = MultilineString.shift_left("""
        my_page       QWidget
          layout      QVBoxLayout
            foo       QPushButton(Hello)
            bar       QPushButton(World)
    """)

    @classmethod
    def setUpClass(cls):
        cls._input_file_dir = tempfile.mkdtemp()

    def tearDownClass(cls):
        shutil.rmtree(cls._input_file_dir)

    @classmethod
    def setUp(cls):
        if qApp is not None:
            qApp.quit()
        cls.re_init_input_files()

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def _re_init_input_files(cls):
        for name in (cls._SIMPLE,):
            cls._make_input_file(name)

    @classmethod
    def _make_input_file(cls, name):
        file_path = os.path.join(cls._input_file_dir, name)
        with open(file_path, 'w') as file_to_write:
            file_to_write.write(cls._input_file_content[name])


    def basics_when_working_normally_test(self):
        QApplication([])

        # Bring up App in its clean virgin state
        app = HelperGui()

        # Press the CHOOSE FILE button in the gui, providing a monkey
        # patched mocked file chooser.
        app._set_file_chooser_callback(
                lambda name=self._SIMPLE: self._provide_file(name))
        app.path_button.clicked.emit()

        # Wait few secs for the automatic build to take place.
        QTimer() fart got to here, need to persist timer
        but how keep separate?
        # now can inspect entire steady state of app gui and what its has built

        # wait a bit more
        # ensure timer fired but concluded no change

        # mutate input file
        # wait bit longer
        # ensure changes reflected everywhere should be

    def error_handling_when_builder_fails_test(self):
        # similar to above but mutate input file to false state

    def simulate_user_changing_to_a_different_path_test(self):
        pass

    def ensure_previous_path_is_remembered_test(self):
        pass

    def error_handling_when_input_file_is_locked_test(self):
        pass

    def copes_with_layout_as_well_as_widget_test(self):
        pass

    def timer_copes_with_no_input_file_set_test(self):
        pass

    def reformat_option_works_test(self):
        pass

    def reformat_declines_when_wont_build_test(self):
        pass

    def copes_with_very_short_paths_test(self):
        pass
