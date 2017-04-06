"""
This module is responsible for dividing text input content into records
by splitting it into fragments like this: 'HBOX:my_box  leftpart middlepart rightpart'.

A definition of the parsing 'contract' can be found in external documentation.
"""

import re

from qtlayoutbuilder.api.filelocation import FileLocation
from qtlayoutbuilder.lib.directorysearch import find_all_files
from qtlayoutbuilder.lib.inputtextrecord import InputTextRecord
from qtlayoutbuilder.api.layouterror import LayoutError


_COMMENT_REGEX = re.compile(r'{[^}]*}')

def _split_file_into_records(file_path):
    """
    This function splits the contents of the given file into records.
    :param file_path: The full path of the file to be split.
    :return: InputTextRecord(s)
    :raises LayoutError
    """

    # Get the text lines from the file.
    try:
        with open(file_path, 'r') as my_file:
            lines = my_file.readlines()
    except Exception as e:
        raise LayoutError(str(e), None)

    # Work through the lines, and the words therein, starting a new record each time
    # a colon word is encountered
    records = []
    line_number = 0
    current_record = None
    for line in lines:
        line_number += 1
        stripped_line = line.strip()
        words = stripped_line.split()
        for word in words:
            if ':' in word:
                # Start new record.
                current_record = InputTextRecord.make_from_lhs_word(
                    word, FileLocation(file_path, line_number))
                records.append(current_record)
            else:
                if len(records) == 0:
                    raise LayoutError(
                        'The first word in your file must have a colon in it: <%s>' % file_path, None)
                current_record.add_child_name(word)
    # Nothing found?
    if len(records) == 0:
        raise LayoutError(
            'Nothing found in this file: <%s>' % file_path, None)
    return records


def _split_big_string_into_records(big_string):
    """
    This function splits the contents of the given string into records.
    :param big_string: The string to split
    :return: InputTextRecord(s)
    :raises LayoutError
    """
    # In this case we can't do anything useful with line numbers, so the
    # easiest way to deal with comments - is to remove them completely
    # before we start.
    big_string = _remove_whole_comments_from(big_string)

    # Now parsing can ignore comments.
    stripped_string = big_string.strip()
    words = stripped_string.split()
    records = []
    current_record = None
    for word in words:
        if ':' in word:
            # Start new record.
            current_record = InputTextRecord.make_from_lhs_word(
                word, FileLocation('direct text provided', 0))
            records.append(current_record)
        else:
            if len(records) == 0:
                raise LayoutError('Error: The first word in your text must have a colon in it: <%s>' % big_string, None)
            current_record.add_child_name(word)
    return records


def _split_all_files_in_directory_into_records(directory_path):
    """
    This function splits the contents of all the files in the given directory,
    and sub directories (recursively).
    :param directory_path: The full path of the directory to be split.
    :return: InputTextRecord(s)
    :raises LayoutError
    """
    files = find_all_files(directory_path)
    all_records = []
    for file_to_split in files:
        records = _split_file_into_records(file_to_split)
        all_records.extend(records)
    return all_records

def _remove_whole_comments_from(big_string):
    return _COMMENT_REGEX.sub('', big_string)
