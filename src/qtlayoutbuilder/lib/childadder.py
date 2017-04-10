"""
This module provides a generalised function that tries various adventures,
to add a child to a Qt parent object. See the code below for the logical
experiments it tries.
"""

from exceptions import RuntimeError

from PySide.QtGui import QLayout, QWidget

from qtlayoutbuilder.api.layouterror import LayoutError


class ChildAdder(object):

    @classmethod
    def add_child_to_parent(cls, child_name, parent_object,
            child_object_lookup_dict, record):
        """
        Attempts to add the child whose name is provided to the QObject parent
        provided, using a combination of speculative method calls.
        See implementation for the logic of these.
        :param child_name: The name of the child.
        :param parent_object: The parent QObject.
        :param child_object_lookup_dict: A dictionary in which the child name
        can be looked up to see if it has been previously reconciled to an
        existing QObject.
        :param record: The InputTextRecord that defines this parent child.
        :return: None
        :raises: LayoutError - when none of the recipes yields fruit.
        """

        # The special case first - when the child is not registered it is taken as
        # literal text that should be given to the parent with a setText() call.
        if child_name not in child_object_lookup_dict:
            cls._add_child_text(child_name, parent_object, record)
            return

        # Now the general cases of children being widgets or layouts.
        child_object = child_object_lookup_dict[child_name]
        # Stop at the first method from the experimental sequence, which
        # the parent object has (as a callable), and which does not raise
        # exceptions when it is called.
        for method_name in _SPECULATIVE_METHODS:
            method = cls._get_method(parent_object, method_name)
            if method is None:
                continue
            try:
                method(child_object)
            except TypeError as e:
                # Maybe calling addWidget() with a QLayout) etc.
                continue
            # If execution gets to here, the method has worked, so we stop.
            break

    # ------------------------------------------------------------------------
    # Private below

    @classmethod
    def _get_method(cls, object, method_name):
        attr = getattr(object, method_name, None)
        if attr is None:
            return None
        if not callable(attr):
            return None
        return attr

    @classmethod
    def _add_child_text(cls, child_name, parent_object, record):
        # Our contract promises to replace double underscores with a space
        # in this context.
        with_spaces = child_name.replace('__', ' ')
        try:
            parent_object.setText(with_spaces)
        except AttributeError as e:
            raise LayoutError(
                '\n'.join([
                    'Because this child name: <%s>, is not defined',
                    'anywhere else in your input as a QObject, we tried',
                    'using it in a call to setText() on the parent.',
                    'But this type of parent does not support setText().',
                ]) % child_name, record.file_location)


_SPECULATIVE_METHODS = (
    'addLayout',
    'setLayout',
    'addWidget',
    'addTab',
)
