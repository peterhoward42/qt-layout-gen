"""
This module is responsible for dividing text input content into records
by splitting it into fragments like this: 'HBOX:my_box  leftpart middlepart rightpart'.

A definition of the parsing 'contract' follows.

This example illustrates all the parsing rules:

    VBOX:my_page                header_row          body            <>
    VBOX:my_page                row_a               row_b           row_c
                                row_d               row_e           row_f
                                row_g
    QVBoxLayout:my_page         row_a               row_b           row_c
    Find:CustomLayout:my_page   header_row          body            footer_row


We simply split it at whitespace to get the constituent 'words'.
A record is deemed to begin at any word that contains a colon.
And to end just before the next word encountered that has a colon,
(or EOF).
"""

from builderror import BuildError
from directorysearch import find_all_files


class _InputTextRecord(object):
    """
    This is the data structure we use for each record found.
    In addition to holding the constituent words, it also holds
    a FileLocation - which remembers the source filename and
    line number to help with error handling later on.
    """

    def __init__(self, file_location, words):
        self.file_location = file_location
        self.words = words


def _split_file_into_records(file_path):
    """
    This function splits the contents of the given file into records if it can,
    or returns a BuildError.
    :param file_path: The full path of the file to be split.
    :return: (InputTextRecords, BuildError)
    """

    # Get the text lines from the file.
    try:
        with open(file_path, 'r') as my_file:
            lines = my_file.readlines()
    except Exception as e:
        return None, BuildError(str(e)).extended_with('Cannot split the file <%s> into records' % file_path)

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
                current_record = _InputTextRecord(_FileLocation(file_path, line_number), [word, ])
                records.append(current_record)
            else:
                if len(records) == 0:
                    return None, BuildError(
                        'Error: The first word in your file must have a colon in it: <%s>' % file_path)
                current_record.words.append(word)
    # Nothing found?
    if len(records) == 0:
        return None, BuildError('Error: No records found in this file: <%s>' % file_path)
    return records, None


def _split_big_string_into_records(big_string):
    """
    This is a minor variation on the _split_file_into_records() function above,
    which takes the text to split as a directly injected input.
    """
    stripped_string = big_string.strip()
    words = stripped_string.split()
    records = []
    current_record = None
    for word in words:
        if ':' in word:
            # Start new record.
            current_record = _InputTextRecord(_FileLocation('direct text provided', 0), [word, ])
            records.append(current_record)
        else:
            if len(records) == 0:
                return None, BuildError('Error: The first word in your text must have a colon in it: <%s>' % big_string)
            current_record.words.append(word)
    return records, None


def _split_all_files_in_directory_into_records(directory_path):
    """
    This is a minor variation on the _split_file_into_records() function above,
    which deals with multiple files. It consumes all the files found in the
    directory provided and the sub directories (recursively).
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


class _FileLocation(object):
    """
    A simple container to hold the name of a file and a line number with it.
    """

    def __init__(self, file_name, line_number):
        self.file_name = file_name
        self.line_number = line_number

    def __str__(self):
        return '%s, at line %d' % (self.file_name, self.line_number)
