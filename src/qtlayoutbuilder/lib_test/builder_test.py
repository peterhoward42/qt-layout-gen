from unittest import TestCase

from PySide.QtGui import QLabel, QPushButton, qApp, QApplication

from qtlayoutbuilder.api.filelocation import MOCK_FILELOCATION
from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.api.layoutscreated import LayoutsCreated

from qtlayoutbuilder.lib.builder import Builder
from qtlayoutbuilder.lib.inputtextrecord import InputTextRecord
# noinspection PyProtectedMember
from qtlayoutbuilder.lib.inputsplitter import split_big_string_into_records
from qtlayoutbuilder.test_utils import test_utils


class TestBuilder(TestCase):
    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestBuilder, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists.

    # Start with tests for the lower level utilities inside the module.

    def test_add_child_to_parent_error_handling_for_general_case(self):
        # Try to add a QLabel to a QPushButton - which is not a legitimate
        # combination.
        builder = Builder(NO_RECORDS)
        try:
            dict = {'my_label': QLabel()}
            builder._add_child_to_parent('my_label', QPushButton(),
                    InputTextRecord.mock_record(), dict)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                None of the child addition methods worked
                for this child name: <my_label>,
            """, msg))

    def test_register_method_error_handling(self):
        # Use the same name for more than one parent in the input to lib_test
        # the error reporting about the clash.
        builder = Builder(NO_RECORDS)
        try:
            mock_qobject = None
            layouts_created = LayoutsCreated()
            # Manually patch the LayoutsCreated to know about 'my_layout'.
            layouts_created.layout_element['my_layout'] = None
            layouts_created.provenance['my_layout'] = MOCK_FILELOCATION
            builder._register('my_layout', mock_qobject,
                    InputTextRecord.mock_record(), layouts_created)
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                    You cannot use this name: <my_layout> again, because it
                    has already been used here:
                    """, msg))

    def test_register_method_does_register(self):
        # Make sure that when no errors are encountered, the parents end up
        # properly registered in the LayoutsCreated object produced.
        builder = Builder(NO_RECORDS)
        qobject = QLabel()
        layouts_created = LayoutsCreated()
        builder._register('my_label', qobject, InputTextRecord.mock_record(),
                layouts_created)
        self.assertEqual(layouts_created.layout_element['my_label'], qobject)
        self.assertEqual(layouts_created.provenance['my_label'],
                InputTextRecord.mock_file_location())

    def test_that_attempt_to_settext_on_childless_parents_does_not_crash_if_fails(
            self):
        # noinspection PyUnusedLocal
        records = split_big_string_into_records("""
                some_text:QVBoxLayout
            """)
        builder = Builder(records)
        layouts_created = builder.build()

    def test_error_handling_for_adding_stretch_to_something_illegal(self):
        # noinspection PyUnusedLocal
        records = split_big_string_into_records("""
                my_label:QLabel <>
            """)
        builder = Builder(records)
        try:
            builder.build()
        except LayoutError as e:
            msg = str(e)
            self.assertTrue(test_utils.fragments_are_present("""
                    You cannot add a stretch to a parent that is not a
                    QHBoxLayout, or a QVBoxLayout,
                    """, msg))

    def test_at_api_level(self):
        # Exercise the top level api function with mixed content input. And
        # ensure the expected elements show up in the LayoutsCreated.

        my_button = QPushButton()
        records = split_big_string_into_records("""
                my_box:HBOX my_label <> my_button
                my_label:QLabel this__text
                my_button:Find:QPushButton
            """)
        builder = Builder(records)
        layouts_created = builder.build()

        # Produced the right number of layout elements?
        self.assertEqual(len(layouts_created.layout_element), 3)

        elements = layouts_created.layout_element

        # Of the right types
        self.assertEqual(elements['my_box'].__class__.__name__, 'QHBoxLayout')
        self.assertEqual(elements['my_label'].__class__.__name__, 'QLabel')
        self.assertEqual(elements['my_button'].__class__.__name__,
                'QPushButton')

        # And the text got set on the QLabel (with double underscore subst.)
        self.assertEqual(elements['my_label'].text(), 'this text')

        # And the QHBoxLayout got its stretch in the right place
        box_layout = elements['my_box']
        item = box_layout.itemAt(1)
        self.assertEquals(item.__class__.__name__, 'QSpacerItem')


NO_RECORDS = []
