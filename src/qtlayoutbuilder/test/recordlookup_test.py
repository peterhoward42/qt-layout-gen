from unittest import TestCase

from qtlayoutbuilder.lib.inputsplitter import _split_text_into_records
from qtlayoutbuilder.lib.recordlookup import _RecordLookup


class TestRecordLookup(TestCase):

    def test_objects_to_duplicate_names(self):
        # This input text attempts to create two parents called my_box
        records, err = _split_text_into_records('HBOX:my_box a b VBOX:my_box c d')
        record_lookup = _RecordLookup()
        err = record_lookup._populate(records)
        self.assertIsNotNone(err)
        msg = err.format_as_single_string()
        self.assertTrue('You cannot use the parent name: <my_box>, which is specified here: <unused filename, at line -1>' in msg)
        self.assertTrue('because you already used it here: <unused filename, at line -1>' in msg)

    def test_lookup_works_once_built(self):
        records, err = _split_text_into_records('HBOX:my_box a b VBOX:my_other_box c d')
        record_lookup = _RecordLookup()
        err = record_lookup._populate(records)
        self.assertIsNone(err)
        self.assertEqual(record_lookup.records['my_other_box'].child_name_fields[1], 'd')