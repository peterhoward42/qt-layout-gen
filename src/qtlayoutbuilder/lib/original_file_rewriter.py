import os
import re
from datetime import datetime

import shutil
from PySide.QtGui import QDesktopServices
from os import path

from qtlayoutbuilder.lib.multiline_string_utils import MultilineString


class OriginalFileReWriter(object):
    """
    This class is able to overwrite the original input file provided to
    the constructor with a re-formatted variant of the original, in which
    the type names are neatly aligned in a column.

    It backs up the incumbent version to a time stamped file before doing so.
    And writes a comment into the new one to say where the backup got put.

    To make it aware of the input file contents, you must send it the
    lines in the order you process them (using register_line(),
    and additionally, for those that are amenable to being realigned, you must
    call also register_name().

    You then mandate the overwrite operation by calling
    overwrite_original_file()

    IO exceptions are not caught - by design. Such errors cannot be
    recovered from, and the underlying exceptions provide perfectly lucid
    explanations.
    """

    def __init__(self, original_file_path):
        self._original_file_path = original_file_path
        self._lines = []
        self._required_column_for_type_word = -1

    def register_line(self, line):
        # Just save them at this juncture.
        self._lines.append(line)

    def register_name_for_most_recently_registered_line(self, name):
        # Reminder of a line: '   my_page    QLabel(some text)'

        # As each re-formattable line is received, we replace our copy of the
        # line, with a version that has the whitespace between the name and
        # the type string replaced with a special, (sentinel) token string.
        # At the same time we ratchet up how far to the right the type strings
        # should be aligned, to accomodate the rightmost-reaching name segment.
        line = self._lines.pop()
        end_of_name_index = line.index(name) + len(name) - 1
        if end_of_name_index + self._MIN_GUTTER \
                > self._required_column_for_type_word:
            self._required_column_for_type_word = \
                end_of_name_index +  self._MIN_GUTTER
        regex = re.compile(name + r'\s+')
        anchored_line = regex.sub(name + self._ANCHOR, line, 1)
        self._lines.append(anchored_line)

    def overwrite_original_file(self):
        path_used = self._make_backup_of_existing_file()
        reformatted_lines = self._reformat_content()
        with open(self._original_file_path, 'w') as output_file:
            output_file.writelines(reformatted_lines)


    #------------------------------------------------------------------------
    # Private below.

    def _make_backup_of_existing_file(self):
        # We ask Qt for a suitable directory on the platform for user data.
        # On Windows it will resolve to something like:
        # C:\Users\<user_namer>\AppData\Local\python\qtlayoutbuilder\
        # Each file is timestamped like this:
        # archived_input-20170417-003554.txt

        dir_for_archive_copy = path.join(QDesktopServices.storageLocation(
                QDesktopServices.DataLocation), 'qtlayoutbuilder')
        if not os.path.exists(dir_for_archive_copy):
            os.makedirs(dir_for_archive_copy)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive_fname = path.join(
                dir_for_archive_copy, 'archived_input-' + timestamp + '.txt')
        shutil.copyfile(self._original_file_path, archive_fname)
        return archive_fname

    def _reformat_content(self):
        new_lines = []
        for line in self._lines:
            if self._ANCHOR in line:
                output_line = self._adjust_line(line)
            else:
                output_line = line
            new_lines.append(output_line + '\n')
        return new_lines

    def _adjust_line(self, line):
        # Adjustable lines have the space between their name word and their
        # type string replaced with an ANCHOR token.
        name_ends_at = line.index(self._ANCHOR) -1
        length_of_name_part = name_ends_at + 1
        spacing = self._required_column_for_type_word - length_of_name_part
        filler = ' ' * spacing
        new_line = line.replace(self._ANCHOR, filler)
        return new_line

    _ANCHOR = '6JNjcx3vEQ'
    _MIN_GUTTER = 6
