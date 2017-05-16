"""
This module provides a generalised function that tries various adventures,
to add a child to a Qt parent object. See the code below for the logical
experiments it tries.
"""
from PySide.QtCore import Qt
from PySide.QtGui import QScrollArea, QSlider

from qtlayoutbuilder.api.layouterror import LayoutError


class ChildAdder(object):
    # Used for the tab name if addTab() is called.
    _next_tab_number = 0

    @classmethod
    def add(cls, child_object, child_name, parent_object):
        # Stop at the first method from the experimental sequence, which
        # the parent object has, and which does not raise  exceptions when it
        # is called.
        for method_name in _SPECULATIVE_METHODS:
            if cls._method_worked(method_name, child_object, parent_object):
                return
        # Nothing worked, which is an error
        raise LayoutError("""
            Could not add this child: <%s> to its parent.
            The child is a: <%s>
            The parent is a: <%s>

            None of the following addition methods worked:

            %s
            """, (child_name, child_object.__class__.__name__,
                  parent_object.__class__.__name__,
                  cls._format_supported_add_methods()))

    @classmethod
    def _method_worked(cls, method_name, child_object, parent_object):
        # Does this parent have this method?
        method = cls._get_method(parent_object, method_name)
        if method is None:
            return False
        # The method is available and callable - let's see if it
        # complains.
        try:
            # Some addition methods require a bit of intervention.
            if method_name == 'addTab':  # QTabWidget
                cls._next_tab_number += 1
                method(child_object, 'tab_%d' % cls._next_tab_number)
            else:  # General case.
                method(child_object)

            # We promise a few post-addition actions for some child or
            # parent types.
            if isinstance(parent_object, QScrollArea):
                parent_object.setWidgetResizable(True)
            if isinstance(child_object, QSlider):
                child_object.setOrientation(Qt.Orientation.Horizontal)

            return True  # The method worked.
        except TypeError:
            return False

    @classmethod
    def _get_method(cls, target_object, method_name):
        attr = getattr(target_object, method_name, None)
        if attr is None:
            return None
        if not callable(attr):
            return None
        return attr

    @classmethod
    def _format_supported_add_methods(cls):
        return '\n'.join(_SPECULATIVE_METHODS)


_SPECULATIVE_METHODS = (
    'addLayout', 'setLayout', 'addWidget', 'addTab', 'setWidget',
    'addSpacerItem',)
