"""
A module providing utility functions that make it easier to write tests
that examine multi-line error messages.
"""

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