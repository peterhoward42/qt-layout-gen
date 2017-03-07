from unittest import TestCase

import os.path

from PySide.QtGui import QLabel

from buildlayouts import _reconcile_child_to_object
# noinspection PyProtectedMember
from inputsplitter import _split_text_into_records  # noinspection PyProtectedMember
from recordlookup import _RecordLookup


class TestBuildLayouts(TestCase):
    def test_reconcile_child_to_object_error_handling(self):
        # Note that 'outer_box' calls for 'right_box' as a child.
        records, err = _split_text_into_records(
            """
                HBOX:outer_box  left_box    right_box
                VBOX:left_box   left_a      left_b
                VBOX:right_box  right_a     right_b
            """)
        self.assertIsNone(err)

        # Provide a register that doesn't know about 'right_box'
        register = {}

        # Ask the reconciler to reconcile 'right_box' in the context of the
        # appropriate text input record.
        record_lookup = _RecordLookup()
        err = record_lookup._populate(records)
        self.assertIsNone(err)
        outer_box_record = record_lookup.records['outer_box']
        q_object, err = _reconcile_child_to_object('right_box', outer_box_record, register)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('Nothing found in register for this child name: <right_box>' in msg)
        self.assertTrue('defined at: <unused filename, at line -1>' in msg)

    def test_reconcile_child_to_object_succeeding(self):
        # Note that 'outer_box' calls for 'right_box' as a child.
        records, err = _split_text_into_records(
            """
                HBOX:outer_box  left_box    right_box
                VBOX:left_box   left_a      left_b
                VBOX:right_box  right_a     right_b
            """)
        self.assertIsNone(err)

        # Make a mock register that knows how to resolve 'outer_box', and assert that
        # the child in the record that calls for it is satisfied thus.
        mock_object = {}
        register = {'right_box': mock_object}

        # Ask the reconciler to reconcile 'right_box' in the context of the
        # appropriate text input record.

        record_lookup = _RecordLookup()
        err = record_lookup._populate(records)
        self.assertIsNone(err)
        outer_box_record = record_lookup.records['outer_box']
        q_object, err = _reconcile_child_to_object('right_box', outer_box_record, register)
        self.assertEqual(q_object, mock_object)
