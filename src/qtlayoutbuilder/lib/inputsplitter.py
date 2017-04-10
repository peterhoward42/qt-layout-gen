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

_COMMENT_REGEX = re.compile(r'#.*')

def split_file_into_records(file_path):
    """
    This function splits the contents of the given file into records.
    :param file_path: The string to split
    :return: InputTextRecord(s)
    :raises LayoutError
    """
    lines = _get_lines_from_file(file_path)
    splitter = _SplitLinesIntoRecords(lines, file_path)
    return splitter.split()

def split_big_string_into_records(big_string):
    """
    This function splits the contents of the given string into records.
    :param big_string: The string to split
    :return: InputTextRecord(s)
    :raises LayoutError
    """
    lines = big_string.split('\n')
    splitter = _SplitLinesIntoRecords(lines, 'unspecified file')
    return splitter.split()


def split_all_files_in_directory_into_records(directory_path):
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
        records = split_file_into_records(file_to_split)
        all_records.extend(records)
    return all_records

#----------------------------------------------------------------------------
# Private below.

class _SplitLinesIntoRecords(object):
    # We use a class for this because the splitting process is stateful, and
    # the class gives us somewhere nicecly encapsulated to hold this state.

    def __init__(self, lines, file_path):
        """
        The file_path is used only for error reporting (it is not read here).
        Use 'unspecified' or similar when the input did not come from a file.
        """
        self._file_path = file_path
        self._lines = lines
        self._records = []  # Accumulator.
        self._line_number = None  # Line number in file, starting at 1.

    def split(self):
        """
        Carries out the split operation and returns the records created.
        :return: [InputTextRecord, InputTextRecord, ...]
        :raises: LayoutError
        """
        self._line_number = 0
        for line in self._lines:
            self._line_number += 1
            self._consume_line(line)
        self._assert_some_records_found()
        return self._records

    def _consume_line(self, line):
        line = _remove_comments_from_line(line)
        words = self._words_from_line(line)
        for word in words:
            # Start new record when encounter a word that contains a colon.
            if ':' in word:
                self._records.append(
                        InputTextRecord.make_from_lhs_word(
                                word, FileLocation(self._file_path, self._line_number)))
            else:
                self._assert_first_word_encountered_is_colon_word()
                self._get_current_record().add_child_name(word)


    def _assert_some_records_found(self):
        if len(self._records) == 0:
            raise LayoutError(
                    'Nothing found in this file: <%s>' % self._file_path, None)

    def _words_from_line(self, line):
        stripped_line = line.strip()
        words = stripped_line.split()
        return words

    def _get_current_record(self):
        return self._records[len(self._records) - 1]

    def _assert_first_word_encountered_is_colon_word(self):
        if len(self._records) == 0:
            raise LayoutError(
                    'The first word of your input must have a colon in it: '
                    '<%s>' %
                    self._file_path, None)

def _get_lines_from_file(file_path):
    try:
        with open(file_path, 'r') as my_file:
            lines = my_file.readlines()
            return lines
    except Exception as e:
        raise LayoutError(str(e), None)

def _remove_comments_from_line(line):
    return _COMMENT_REGEX.sub('', line)
