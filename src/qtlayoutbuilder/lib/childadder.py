"""
This module provides a generalised function that tries various adventures,
to add a child to a Qt parent object. See the code below for the logical
experiments it tries.
"""

from exceptions import RuntimeError

from PySide.QtGui import QLayout, QWidget

from qtlayoutbuilder.api.layouterror import LayoutError


class ChildAdder(object):
    @staticmethod
    def add_child_to_parent(
            child_name, parent_object, child_object_lookup_dict, record):
        """
        Attempts to add the child whose name is provided to the QObject parent
        provided, using a combination of speculative method calls.
        See implementation for the logic of these.
        :param child_name: The name of the child.
        :param parent_object: The parent QObject.
        :param child_object_lookup_dict: A dictionary in which the child name
        can be looked up to see if it has been reconciled to an existing QObject.
        :param record: The InputTextRecord that defines this parent child.
        :return: None
        :raises: LayoutError - when none of the recipes yields fruit.
        """

        # The special case first - when the child is not registered it is taken as
        # literal text that should be given to the parent with a setText() call.
        if child_name not in child_object_lookup_dict:
            ChildAdder._add_child_text(child_name, parent_object, record)
            return

        # Now the general cases of children being widgets or layouts.
        child_object = child_object_lookup_dict[child_name]
        if isinstance(child_object, QWidget):
            ChildAdder._add_child_widget(child_object, child_name,
                                         parent_object, record)
        elif isinstance(child_object, QLayout):
            ChildAdder._add_child_layout(child_object, child_name,
                                         parent_object, record)
        else:
            raise RuntimeError('Coding error.')

    # ------------------------------------------------------------------------
    # Private below

    @staticmethod
    def _add_child_text(child_name, parent_object, record):
        try:
            parent_object.setText(child_name)
        except AttributeError as e:
            raise LayoutError(
                '\n'.join([
                    'Because this child name: <%s>, is not defined',
                    'anywhere else in your input as a QObject, we tried',
                    'using it in a call to setText() on the parent.',
                    'But this type of parent does not support setText().',
                ]) % child_name, record.file_location)

    @staticmethod
    def _add_child_widget(child_object, child_name, parent_object, record):
        success = ChildAdder._try_using_addWidget(child_object, parent_object)
        if success:
            return
        success = ChildAdder._try_using_addTab(
            child_object, child_name, parent_object)
        if success:
            return
        raise LayoutError(
            '\n'.join([
                'This child name: <%s>, is a QWidget',
                'but neither addWidget(), nor addTab() worked',
                'on the parent object.',
            ]) % child_name, record.file_location)

    @staticmethod
    def _add_child_layout(child_object, child_name, parent_object, record):
        success = ChildAdder._try_using_addLayout(child_object, parent_object)
        if success:
            return
        success = ChildAdder._try_using_setLayout(
                child_object, parent_object)
        if success:
            return
        raise LayoutError(
            '\n'.join([
                'This child name: <%s>, is a QLayout',
                'but neither addLayout(), nor setLayout() worked',
                'on the parent object.',
            ]) % child_name, record.file_location)

    @staticmethod
    def _try_using_addWidget(child_object, parent_object):
        try:
            parent_object.addWidget(child_object)
            return True
        except Exception as e:
            return False

    @staticmethod
    def _try_using_addTab(child_object, child_name, parent_object):
        try:
            name_for_tab = child_name
            parent_object.addTab(child_object, name_for_tab)
            return True
        except Exception as e:
            return False

    @staticmethod
    def _try_using_addLayout(child_object, parent_object):
        try:
            parent_object.addLayout(child_object)
            return True
        except Exception as e:
            return False

    @staticmethod
    def _try_using_setLayout(child_object, parent_object):
        try:
            parent_object.setLayout(child_object)
            return True
        except Exception as e:
            return False
