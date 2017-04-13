"""
A module providing utility functions that make it easier to write tests
that examine multi-line error messages.
"""
import difflib

from qtlayoutbuilder.api import LayoutError
from qtlayoutbuilder.lib.string_utils import MultilineString


def fragments_are_present(multiline_string, message):
    """
    First splits the multiline string into fragments, one per line, and strips
    these of leading and trailing whitespace. Then determines if the sequence
    of strings produced are all present somewhere in the given message.
    :param multiline_string: The input multi-line string.
    :param message: A string.
    :return: Boolean
    """
    fragments = _clean_up(multiline_string)
    for fragment in fragments:
        if fragment not in message:
            return False
    return True

def _clean_up(multi_line_string):
    """
    Splits a multi-line string into a sequence of strings - one per line,
    with each constituent line having all white space removed from both ends.
    :param multi_line_string: The input multi-line string.
    :return: A sequence of strings.
    """
    lines = multi_line_string.split('\n')
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if len(line) > 0]
    return lines

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
            print 'xxxx messages the same, returning true'
            return True
        else:
            print 'xxxx messages differ, returning False'
            return False
    # If we reach here, the message produces does not match that required.
    print 'xxxxx dont think will get here'
    return False
