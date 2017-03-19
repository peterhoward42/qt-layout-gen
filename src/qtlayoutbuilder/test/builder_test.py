from unittest import TestCase

from PySide.QtGui import QLabel, QPushButton, qApp, QApplication

from qtlayoutbuilder.api.filelocation import MOCK_FILELOCATION
from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.api.layoutscreated import LayoutsCreated

from qtlayoutbuilder.lib.builder import Builder
from qtlayoutbuilder.lib.inputtextrecord import InputTextRecord
from qtlayoutbuilder.lib.inputsplitter import _split_big_string_into_records


class TestBuilder(TestCase):

    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestBuilder, cls).setUpClass()
        if qApp is None:
            QApplication([])

    # Start with tests for the lower level utilities inside the module -
    # providing a mocked environment.

    def test_add_child_to_parent_error_handling(self):
        # Add an unsupported combination.
        builder = Builder(NO_RECORDS)
        try:
            builder._add_child_to_parent(
                QLabel(), QPushButton(), _arbitrary_record())
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'The builder does not know how to add a: <QLabel>, to a:'
                in msg)
            self.assertTrue(
                '<QLabel> as a child.'
                in msg)
            self.assertTrue(
                'This combination is not supported.'
                in msg)

    def test_register_method_error_handling(self):
        # Try to register a name that is already known.
        builder = Builder(NO_RECORDS)
        try:
            mock_qobject = None
            layouts_created = LayoutsCreated()
            # Manually patch the LayoutsCreated to know about 'my_layout'.
            layouts_created.layout_element_from_name['my_layout'] = None
            layouts_created.source_file_location_from_name['my_layout'] = MOCK_FILELOCATION
            builder._register('my_layout', mock_qobject, _arbitrary_record(), layouts_created)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'You cannot use this name: <my_layout> again, because it'
                in msg)
            self.assertTrue(
                'has already been used here: <no-such-file, at line -1>,'
                in msg)

    def test_register_method_does_register(self):
        builder = Builder(NO_RECORDS)
        qobject = QLabel()
        layouts_created = LayoutsCreated()
        builder._register('my_label', qobject, _arbitrary_record(), layouts_created)
        self.assertEqual(
            layouts_created.layout_element_from_name['my_label'], qobject)
        self.assertEqual(
            layouts_created.source_file_location_from_name['my_label'],
            MOCK_FILELOCATION)

    def test_assert_name_is_registered_error_handling(self):
        builder = Builder(NO_RECORDS)
        try:
            mock_qobject = None
            layouts_created = LayoutsCreated()
            builder._assert_name_is_registered(
                'my_layout', _arbitrary_record(), layouts_created)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'You cannot use this name: <my_layout>, because it'
                in msg)
            self.assertTrue(
                'is not defined anywhere in your input., (no-such-file, at line -1)'
                in msg)

    def test_assert_name_is_registered_when_the_name_is(self):
        builder = Builder(NO_RECORDS)
        layouts_created = LayoutsCreated()
        # Manually patch the LayoutsCreated to know about 'my_layout'.
        layouts_created.layout_element_from_name['my_layout'] = None
        layouts_created.source_file_location_from_name['my_layout'] = MOCK_FILELOCATION
        builder._assert_name_is_registered(
                'my_layout', _arbitrary_record(), layouts_created)

    def test_at_api_level(self):
        my_button = QPushButton()
        records = _split_big_string_into_records(
            """
                HBOX:my_box my_label my_button
                QLabel:my_label
                Find:QButton:my_button
            """)
        builder = Builder(records)
        layouts_created = builder.build()
        self.assertEqual(len(layouts_created.layout_element_from_name), 3)


NO_RECORDS = []

def _arbitrary_record():
    words = ['QLabel:my_label', 'a', 'b']
    record = InputTextRecord.make_from_all_words(words, MOCK_FILELOCATION)
    return record
