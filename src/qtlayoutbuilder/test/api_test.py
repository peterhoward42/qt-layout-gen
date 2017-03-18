from unittest import TestCase

import os.path

from qtlayoutbuilder.api import build_layouts_from_dir


class TestApi(TestCase):

    def test_just_a_runner(self):
        directory = os.path.abspath(os.path.join(
            __file__, "../../..", 'testdata', 'simple_hierarchy'))

        layouts, err = build_layouts_from_dir(directory)
        msg = err.format_as_single_string()
        print msg