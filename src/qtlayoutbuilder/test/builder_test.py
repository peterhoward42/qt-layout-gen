from unittest import TestCase

from PySide.QtGui import QLabel, QPushButton, qApp, QApplication

from qtlayoutbuilder.api.filelocation import MOCK_FILELOCATION
from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.api.layoutscreated import LayoutsCreated

from qtlayoutbuilder.lib.builder import Builder
from qtlayoutbuilder.lib.inputtextrecord import InputTextRecord
# noinspection PyProtectedMember
from qtlayoutbuilder.lib.inputsplitter import _split_big_string_into_records


class TestBuilder(TestCase):
    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestBuilder, cls).setUpClass()
        if qApp is None:
            QApplication([])

    # Start with tests for the lower level utilities inside the module.

    def test_add_child_to_parent_error_handling(self):
        # Try to add a QLabel to a QPushButton - which is not a legitimate
        # combination.
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
        # Use the same name for more than one parent in the input to test
        # the error reporting about the clash.
        builder = Builder(NO_RECORDS)
        try:
            mock_qobject = None
            layouts_created = LayoutsCreated()
            # Manually patch the LayoutsCreated to know about 'my_layout'.
            layouts_created.layout_element['my_layout'] = None
            layouts_created.provenance['my_layout'] = MOCK_FILELOCATION
            builder._register(
                'my_layout', mock_qobject, _arbitrary_record(), layouts_created)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'You cannot use this name: <my_layout> again, because it'
                in msg)
            self.assertTrue(
                'has already been used here: <no-such-file, at line -1>,'
                in msg)

    def test_register_method_does_register(self):
        # Make sure that when no errors are encountered, the parents end up
        # properly registered in the LayoutsCreated object produced.
        builder = Builder(NO_RECORDS)
        qobject = QLabel()
        layouts_created = LayoutsCreated()
        builder._register(
            'my_label', qobject, _arbitrary_record(), layouts_created)
        self.assertEqual(
            layouts_created.layout_element['my_label'], qobject)
        self.assertEqual(
            layouts_created.provenance['my_label'],
            MOCK_FILELOCATION)

    def test_child_name_not_recognized(self):
        # Use a child name in the input which the builder won't be able to
        # reconcile to a parent that has been created by another record, to
        # test the error handling in this case.
        builder = Builder(NO_RECORDS)
        try:
            layouts_created = LayoutsCreated()
            builder._assert_name_is_registered(
                'my_layout', _arbitrary_record(), layouts_created)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(
                'You cannot use this name: <my_layout>, because it'
                in msg)
            self.assertTrue(
                'is not defined anywhere in your input' in msg)

    def test_assert_name_is_registered_when_the_name_is(self):
        # Make sure that when a child name can be properly reconciled
        # to a parent that has been made by another record, it is.
        builder = Builder(NO_RECORDS)
        layouts_created = LayoutsCreated()
        # Manually patch the LayoutsCreated to know about 'my_layout'.
        layouts_created.layout_element['my_layout'] = None
        layouts_created.provenance['my_layout'] = MOCK_FILELOCATION
        builder._assert_name_is_registered(
            'my_layout', _arbitrary_record(), layouts_created)

    def test_at_api_level(self):
        # Exercise the top level api function with mixed content input. And
        # ensure the expected elements show up in the LayoutsCreated.

        # noinspection PyUnusedLocal
        my_button = QPushButton()
        records = _split_big_string_into_records(
            """
                HBOX:my_box my_label my_button
                QLabel:my_label
                Find:QPushButton:my_button
            """)
        builder = Builder(records)
        layouts_created = builder.build()
        self.assertEqual(len(layouts_created.layout_element), 3)


NO_RECORDS = []


def _arbitrary_record():
    words = ['QLabel:my_label', 'a', 'b']
    record = InputTextRecord.make_from_all_words(words, MOCK_FILELOCATION)
    return record
