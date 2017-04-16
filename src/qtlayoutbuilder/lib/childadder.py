"""
This module provides a generalised function that tries various adventures,
to add a child to a Qt parent object. See the code below for the logical
experiments it tries.
"""
from qtlayoutbuilder.api.layouterror import LayoutError


class ChildAdder(object):

    # Used for the tab name if addTab() is called.
    _next_tab_number = 0

    @classmethod
    def add(cls, child_object, child_name, parent_object):
        # Stop at the first method from the experimental sequence, which
        # the parent object has (as a callable), and which does not raise
        # exceptions when it is called.
        for method_name in _SPECULATIVE_METHODS:
            # Does this parent have this method?
            method = cls._get_method(parent_object, method_name)
            if method is None:
                continue
            # The method is available and callable - let's see if it
            # complains.
            try:
                # Calling addTab() needs a string argument as well as the
                # child object.
                if method_name == 'addTab':
                    cls._next_tab_number += 1
                    method(child_object, 'tab_%d' % cls._next_tab_number)
                else:  # General case.
                    method(child_object)
                # If we get to here, the method worked, so we stop.
                return
            except TypeError as e:
                # Maybe calling addWidget() with a QLayout) etc.
                # In which case move on to try the next method.
                continue
        # Nothing worked, which is an error
        raise LayoutError("""
            Could not add this child: <%s> to its parent.
            The child is a: <%s>
            The parent is a: <%s>

            None of the following addition methods worked:

            %s
            """,
            (child_name, child_object.__class__.__name__,
             parent_object.__class__.__name__,
             cls._format_supported_add_methods()))

    @classmethod
    def _get_method(cls, object, method_name):
        attr = getattr(object, method_name, None)
        if attr is None:
            return None
        if not callable(attr):
            return None
        return attr

    @classmethod
    def _format_supported_add_methods(cls):
        return '\n'.join(_SPECULATIVE_METHODS)


_SPECULATIVE_METHODS = (
'addLayout',
'setLayout',
'addWidget',
'addTab',
'setWidget',
)
