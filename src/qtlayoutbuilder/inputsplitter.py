"""
This module is responsible for splitting text input content into records
by splitting it at LayoutKeywords like HBOX, and harvesting the strings that
follow the keyword before the next one is reached.
"""

import re

from builderror import BuildError
from layoutkeywords import KEYWORD_ALTERNATIVES_REGEX

# Note this module is laid out in a bottom-up fashion, starting with lower level
# utilities and then as it goes down, combining them into higher level operations.

class _FileLocation(object):
    """
    A simple container to hold the name of a file and a line number with it.
    """

    def __init__(self, file_name, line_number):
        self.file_name = file_name
        self.line_number = line_number

    def __str__(self):
        return '%s, at line %d' % (self.file_name, self.line_number)


class _InputTextRecord(object):
    """
    A container to hold the text fields from a single input text record in a structured form.
    I.e. a structured form of "VBOX:my_box top middle bottom".
    Also its corresponding FileLocation object to aid error reporting.
    """

    def __init__(self, file_location, layout_keyword, parent_name, child_name_fields):
        self.file_location = file_location
        self.layout_keyword = layout_keyword
        self.parent_name = parent_name
        self.child_name_fields = child_name_fields


def _make_one_input_text_record(input_text_fragment, file_location):
    """
    Creates one InputTextRecord from the given input text fragment when it can, or
    returns a non-None BuildError. Applies plausibility checks to the text
    provided.
    :param input_text_fragment: A string like this: "VBOX:my_box top middle bottom"
    :param file_location: Injected provenance information to be included in
    any error reporting.
    :return: (InputTextRecord, BuildError).
    """
    keyword_match = KEYWORD_ALTERNATIVES_REGEX.match(input_text_fragment)
    if not keyword_match:
        return None, BuildError('Cannot find keyword at beginning of this string: %s' % input_text_fragment)
    keyword_found = keyword_match.group()
    remainder = input_text_fragment.replace(keyword_found, '')
    if not remainder.startswith(':'):
        return None, BuildError('Expected colon (:) after keyword in this string: %s' % input_text_fragment)
    remainder = remainder[1:]
    # Should just be whitespace separated names now
    names = remainder.split()
    if len(names) < 2:
        return None, BuildError(
            'Expected at least two names after the colon (:) in this string: %s' % input_text_fragment)
    for name in names:
        if fart got to here is a word

    """
    capture the leading keyword and replace it with nothing
    demand that a colon follows and remote it
    demand that what follows is at least two names
    extract and remove the first, demanding that it be a good word
    demand that the others are good words
    package and return the record
    """


# These are used in some search, replace and splitting logic just below.
_SENTINEL_STRING = r'z8g3b7h6n3' # arbitrary and hopefully never encountered by fluke in real input.
_SENTINEL_REGEX = re.compile(_SENTINEL_STRING)


def _split_text(input_text):
    """
    Provides the sequence of InputTextRecords produced when the given input text is
    split at LayoutKeywords, (or returns a non-None BuildError). The error checks
    make sure there is a well formed name provided for the LHS parent (e.g. 'my_box'),
    and that at least one plausible looking child name follows.
    :param input_text: A string containing an arbitrary number of input records.
    :return: (InputTextRecords, BuildError).
    """

    # Stick a sentinel delimiter just before each recognized keyword (like HBOX).
    # This uses a regex search and replace, that calls out to a replacer helper function.
    # The replacer function leaves the keyword in situ, but tacks the sentinel string in
    # front of it.
    replacement_maker_fn = lambda match: _SENTINEL_STRING + match.group()
    with_sentinels_added = KEYWORD_ALTERNATIVES_REGEX.sub(replacement_maker_fn, input_text)

    # Now if we split the result of that using the sentinel as the delimiter, each segment
    # will start with one of our keywords, and span up to the next one.
    fragments = _SENTINEL_REGEX.split(with_sentinels_added)

    if len(fragments) == 0:
        return [], BuildError('Failed to find any keywords in this text: %s' % input_text)
    records = []
    unused_file_location = _FileLocation('unused filename', -1)
    for fragment in fragments:
        record, err = _make_one_input_text_record(fragment, unused_file_location)
        if err:
            return [], err.extended_with('Could not split this text: %s' % input_text)
        records.append(record)
    return records, None
