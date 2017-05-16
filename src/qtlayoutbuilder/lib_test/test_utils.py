"""
A module providing utility functions that make it easier to write tests
that examine multi-line error messages.
"""
from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib import string_utils
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString


def raises_layout_error_with_this_message(
        required_message, this_callable, *args, **kwargs):
    """
    Makes sure that the callable object provided, when called with *args and
    **kwargs, raises a LayoutException, and that the exception's string
    representation matches that specified in required_message. The message
    equality checking copes with multiline strings and massages these before
    comparison to unify minor differences in whitespace and indentation.
    """
    try:
        this_callable(*args, **kwargs)
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

def raises_layout_error_with_this_approximately_this_message(
        required_message, this_callable, *args, **kwargs):
    """
    Identical to raises_layout_error_with_this_message, except that it
    ignores ALL whitespace in both the required_message and the exception
    report. This is for when you can't easily express the required message in
    a test because part of the string is too long to comply with PEP8. Like
    long exception messages from python that are being re-reported.
    """
    try:
        this_callable(*args, **kwargs)
        # If reach here, it didn't raise the exception.
        return False
    except LayoutError as e:
        error_msg = MultilineString.normalise(str(e))
        error_msg = string_utils.with_all_whitespace_removed(error_msg)
        required_message = \
            string_utils.with_all_whitespace_removed(
                    MultilineString.normalise(required_message))
        if error_msg == required_message:
            return True
    # If we reach here, the message produces does not match that required.
    print 'Message produced was\n%s' % error_msg
    return False
