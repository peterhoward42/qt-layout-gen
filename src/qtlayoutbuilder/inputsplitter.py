"""
This module is responsible for splitting text input content into records
by splitting it into fragments like this: 'HBOX:my_box  leftpart middlepart rightpart'.
In what follows we use the word fragment to refer to this in its raw text form, and
there is a class defined _InputTextRecord for the structured representation.
"""

import re

from builderror import BuildError
from layoutkeywords import KEYWORD_ALTERNATIVES_REGEX  # HBOX or VBOX or TAB etc.


# The module is laid out in a bottom-up fashion, starting with lower level
# utilities.

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
    A container to hold the text fields from a input text fragment in a structured form.
    Also its corresponding FileLocation object to aid error reporting.
    """

    def __init__(self, file_location, layout_keyword, parent_name, child_name_fields):
        self.file_location = file_location
        self.layout_keyword = layout_keyword
        self.parent_name = parent_name
        self.child_name_fields = child_name_fields


_IDENTIFIER = r'^[^\d\W]\w*\Z'
_IDENTIFIER_REGEX = re.compile(_IDENTIFIER)


def _check_validity_of_name(name):
    """
    Does the given name look like a sensible identifier?
    :param name: The name to check (string)
    :return: A BuildError or None.
    """
    if _IDENTIFIER_REGEX.match(name):
        return None
    return BuildError('Name: <%s> is not a valid identifier.' % name)


def _check_names(names):
    """
    Checks the list of names given for plausibility. There must be at least 2,
    and they should like like identifiers.
    :param names: A list of names (strings).
    :return: A BuildError, or None
    """
    if len(names) < 2:
        return BuildError('Expected at least two names')
    for name in names:
        err = _check_validity_of_name(name)
        if err:
            return err.extended_with('Problem with one of the names.')
    return None


def _make_text_record_from_fragment(input_text_fragment, file_location):
    """
    Creates one InputTextRecord from the given input text fragment when it can, or
    returns a non-None BuildError otherwise. Applies plausibility checks to the text
    provided.
    :param input_text_fragment: A string that should start with a keyword like HBOX and
    have the rest of the record's expected content in the remainder.
    :param file_location: Injected to aid error reporting.
    :return: (InputTextRecord, BuildError).
    """

    # Deal with the keyword at the front
    keyword_found = KEYWORD_ALTERNATIVES_REGEX.match(input_text_fragment)
    if not keyword_found:
        return None, BuildError('Cannot find keyword at beginning of this string: %s' % input_text_fragment)
    keyword = keyword_found.group()

    # Make sure a colon comes next
    remainder = input_text_fragment.replace(keyword, '')
    if not remainder.startswith(':'):
        return None, BuildError('Expected colon (:) after keyword in this string: %s' % input_text_fragment)

    # Sanity check the list of names that should make up the remainder.
    remainder = remainder[1:]
    names = remainder.split()
    err = _check_names(names)
    if err:
        return None, err.extended_with(
            'Problem with names in this input text fragment: <%s>, at this file location: <%s>)' %
            (input_text_fragment, str(file_location)))

    name_of_parent = names[0]
    names_of_children = names[1:]
    return _InputTextRecord(file_location, keyword, name_of_parent, names_of_children), None


# These are used for some search and replace logic just below.
_SENTINEL_STRING = r'z8g3b7h6n3'  # arbitrary and hopefully never encountered by fluke in real input.
_SENTINEL_REGEX = re.compile(_SENTINEL_STRING)


def _split_text_into_records(input_text):
    """
    Provides the sequence of InputTextRecords produced when the given input text is
    split at LayoutKeywords, (or returns a non-None BuildError). The error checks
    make sure there is a well formed name provided for the LHS parent (e.g. 'my_box'),
    and that at least one plausible looking child name follows.
    :param input_text: A string containing an arbitrary number of input fragments.
    :return: (InputTextRecords, BuildError).
    """

    # Stick a sentinel delimiter just before each recognized keyword (like HBOX).
    # This uses a regex search and replace, that calls out to a replacer helper function.
    # The replacer function leaves the keyword in situ, but tacks the sentinel string in
    # front of it.
    def replacement_maker_fn(match): return _SENTINEL_STRING + match.group()
    with_sentinels_added = KEYWORD_ALTERNATIVES_REGEX.sub(replacement_maker_fn, input_text)

    # Now if we split the result of that using the sentinel as the delimiter, each segment
    # will start with one of our keywords, and span up to the next one.
    fragments = _SENTINEL_REGEX.split(with_sentinels_added)

    if len(fragments) == 0:
        return [], BuildError('Failed to find any keywords in this text: %s' % input_text)
    records = []
    # When all we are given is anonymous text, we have no file source information.
    unused_file_location = _FileLocation('unused filename', -1)
    for fragment in fragments:
        record, err = _make_text_record_from_fragment(fragment, unused_file_location)
        if err:
            return [], err.extended_with('Could not split this text: %s' % input_text)
        records.append(record)
    return records, None