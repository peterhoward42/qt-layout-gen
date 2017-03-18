from unittest import TestCase

from qtlayoutbuilder.lib.buildlayouts import _reconcile_child_to_object, _build_and_register_record
from qtlayoutbuilder.lib.inputsplitter import _split_text_into_records, _InputTextRecord
from qtlayoutbuilder.lib.recordlookup import _RecordLookup


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

    def test_build_and_register_record_failures_with_children(self):
        # Child cannot be reconciled.
        dummy_file_location = {}
        record = _InputTextRecord(dummy_file_location, 'HBOX', 'name_of_parent', ['child_a', 'child_b'])
        dummy_q_object = {}
        register = {} # Will trigger look up failure.
        err = _build_and_register_record(record, register)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue(
            'Problem building child: <child_a>, in record which is' in msg)
        self.assertTrue(
            'Nothing found in register for this child name: <child_a>, defi' in msg)

    def test_build_and_register_record_failures_with_parent(self):
        dummy_file_location = {}
        record = _InputTextRecord(dummy_file_location, 'HBOX', 'name_of_parent', ['child_a', 'child_b'])
        mock_child = {}
        register = {'child_a': mock_child, 'child_b': mock_child}

        no sure to be other more worth while failures

        # We inject the error condition here by monkey patching the keywords module, so
        # that it fails to instantiate a QHBoxLayout
        fart do it
        err = _build_and_register_record(record, register)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        print msg
        self.assertTrue(
            'wont' in msg)
        self.assertTrue(
            'wont' in msg)
        self.assertTrue(
            'wont' in msg)
        self.assertTrue(
            'wont' in msg)

    def test_build_and_register_record_when_already_available(self):
        dummy_file_location = {}
        record = _InputTextRecord(dummy_file_location, 'HBOX', 'name_of_parent', ['child_a', 'child_b'])
        dummy_q_object = {}
        register = {'name_of_parent': dummy_q_object}
        err = _build_and_register_record(record, register)
        self.assertIsNone(err)
        q_object = register['name_of_parent']
        self.assertIsNotNone(q_object)
        self.assertEqual(q_object, dummy_q_object)
