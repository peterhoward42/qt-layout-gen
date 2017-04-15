"""
A module providing utility functions that make it easier to write tests
that examine multi-line error messages.
"""
from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString


def raises_layout_error_with_this_message(
        required_message, callable, *args, **kwargs):
    """
    Makes sure that the callable object provided, when called with *args and
    **kwargs, raises a LayoutException, and that the exception's string
    representation matches that specified in required_message. The message
    equality checking copes with multiline strings and massages these before
    comparison to unify minor differences in whitespace and indentation.
    """
    try:
        callable(*args, **kwargs)
        # If reach here, it didn't raise the exception.
        return False
    except LayoutError as e:
        error_msg = MultilineString.normalise(str(e))
        required_message = MultilineString.normalise(required_message)
        if error_msg == required_message:
            return True
    # If we reach here, the message produces does not match that required.
    print 'Message produced was\n%s' % error_msg
    return False
