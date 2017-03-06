"""
This module is responsible for dividing text input content into records
by splitting it into fragments like this: 'HBOX:my_box  leftpart middlepart rightpart'.
Note that the whitespace separation can include newline characters so that when the
fragment is written into a file, the list of children can span multiple lines.
In what follows we use the word fragment to refer to this in its raw text form
as a single string, and there is a class defined _InputTextRecord for the structured
representation.
"""

import re

from builderror import BuildError
from keywords import starts_with_keyword, mark_all_keywords_found
from directorysearch import find_all_files


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
    A container to hold the text fields from an input text fragment in a structured form.
    Also its corresponding FileLocation object to aid error reporting.
    """

    def __init__(self, file_location, layout_keyword, parent_name, child_name_fields):
        self.file_location = file_location
        self.layout_keyword = layout_keyword
        self.parent_name = parent_name
        self.child_name_fields = child_name_fields


_IDENTIFIER = r'^[^\d\W]\w*\Z'  # Roughly speaking a legitimate variable name.
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


def _check_name_list_from_record(names):
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
    keyword = starts_with_keyword(input_text_fragment)
    if keyword is None:
        return None, BuildError('Cannot find keyword at beginning of this string: <%s>' % input_text_fragment)

    # Make sure a colon comes next
    remainder = input_text_fragment.replace(keyword, '')
    if not remainder.startswith(':'):
        return None, BuildError('Expected colon (:) after keyword in this string: <%s>' % input_text_fragment)

    # Sanity check the list of names that should make up the remainder.
    remainder = remainder[1:]
    names = remainder.split()
    err = _check_name_list_from_record(names)
    if err:
        return None, err.extended_with(
            'Problem with names in this input text fragment: <%s>, at this file location: <%s>)' %
            (input_text_fragment, str(file_location)))

    name_of_parent = names[0]
    names_of_children = names[1:]
    return _InputTextRecord(file_location, keyword, name_of_parent, names_of_children), None


def _cleaned_up(list_of_strings):
    """
    Cleans up the given list of strings by returning a copy in which the
    strings have had leading and trailing whitespace removed, and strings
    that end up empty are discarded.
    :param list_of_strings: The list of strings to filter.
    :return: The new list.
    """
    new_list = []
    for s in list_of_strings:
        s = s.strip()
        if len(s) == 0:
            continue
        new_list.append(s)
    return new_list


# These are used for some search and replace logic just below.
_MARKER_STRING = r'z8g3b7h6n3'  # arbitrary and hopefully never encountered by fluke in real input.
_MARKER_REGEX = re.compile(_MARKER_STRING)


def _split_text_into_records(input_text):
    """
    Provides the sequence of InputTextRecords produced when the given input text is
    split at LayoutKeywords, (or returns a non-None BuildError). The error checks
    make sure there is a well formed name provided for the LHS parent (e.g. 'my_box'),
    and that at least one plausible looking child name follows.
    :param input_text: A string containing an arbitrary number of input fragments.
    :return: (InputTextRecords, BuildError).
    """

    # Stick a marker string just before each recognized keyword (like HBOX).
    # This uses a regex search and replace, that calls out to a replacer helper function.
    # The replacer function leaves the keyword in situ, but tacks the marker in
    # front of it.
    def replacement_maker_fn(match):
        return _MARKER_STRING + match.group()

    with_markers_added = mark_all_keywords_found(input_text, replacement_maker_fn)

    # Now if we split the modified input text using the marker as a delimiter, each segment
    # will start with one of our keywords, and span up to the next one.
    fragments = _MARKER_REGEX.split(with_markers_added)
    fragments = _cleaned_up(fragments)  # get rid of trailing and leading whitespace and ditch empty fragments.

    if len(fragments) == 0:
        return [], BuildError('Failed to find any keywords in this text: %s' % input_text)
    records = []
    # We can't provide meaningful file locations in this context.
    unused_file_location = _FileLocation('unused filename', -1)
    for fragment in fragments:
        record, err = _make_text_record_from_fragment(fragment, unused_file_location)
        if err:
            return [], err.extended_with('Could not split this text: <%s>' % input_text)
        records.append(record)
    return records, None


def _split_file_into_records(file_path):
    """
    Provides the sequence of InputTextRecords produced when the text in the given file is
    consumed. This is a sister function to _split_text_into_records() - which is documented in
    more detail.
    :param file_path: The full path of the file to be split.
    :return: (InputTextRecords, BuildError)
    """

    # Grab the lines from the file.
    try:
        with open(file_path, 'r') as my_file:
            lines = my_file.readlines()
    except Exception as e:
        return None, BuildError(str(e)).extended_with('Cannot split the file <%s> into records' % file_path)

    # Accumulate fragments by working through the lines and starting a new fragment each time
    # a keyword line is encountered.
    fragments = []
    fragment_line_numbers = []
    line_number = 0
    for line in lines:
        line_number += 1
        stripped_line = line.strip()
        keyword = starts_with_keyword(stripped_line)
        if keyword:
            fragments.append(stripped_line)
            fragment_line_numbers.append(line_number)
        else:
            if len(fragments) == 0:
                return None, BuildError('The first line of your file must start with a keyword: <%s>' % file_path)
            fragment_under_construction = fragments[len(fragments) - 1]
            fragments[len(fragments) - 1] = fragment_under_construction + ' ' + line

    # Now we can delegate out to get a record built from each fragment.
    records = []
    for idx in range(len(fragments)):
        fragment = fragments[idx]
        file_location = _FileLocation(file_path, fragment_line_numbers[idx])
        record, err = _make_text_record_from_fragment(fragment, file_location)
        if err is not None:
            return None, err.extended_with('Error splitting file into records.')
        records.append(record)
    return records, None


def _split_all_files_in_directory_into_records(directory_path):
    """
    This is a thin wrapper around _split_file_into_records(), which operates instead on
    all the files that can be found in a directory (recursively).
    :param directory_path: The full path of the directory of interest.
    :return: (InputTextRecords, BuildError)
    """
    files, err = find_all_files(directory_path)
    if err:
        return None, err.extended_with(
            'Error attempting split all files in your directory into records: <%s>' % directory_path)
    all_records = []
    for file_to_split in files:
        records, err = _split_file_into_records(file_to_split)
        if err:
            return None, err.extended_with(
                'Error attempting to split all files in your directory into records: <%s>' % directory_path)
        all_records.extend(records)
    return all_records, None
