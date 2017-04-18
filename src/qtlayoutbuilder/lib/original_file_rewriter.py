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
    the builder with a re-formatted variant of the original, in which
    the type names are neatly aligned in a column.

    It backs up the incumbent version to a time stamped file before doing so.
    And writes a comment into the new one to say where the backup got put.

    IO exceptions are not caught - by design. Such errors cannot be
    recovered from, and the underlying exceptions provide perfectly lucid
    explanations.
    """

    @classmethod
    def overwrite_original(cls, file_path, replacement_one_big_string):
        backup_folder, backup_file_path = \
            cls._make_backup_of_existing_file(file_path)
        augmented_string = cls._add_backup_location_comment(
                backup_folder, replacement_one_big_string)
        with open(file_path, 'w') as output_file:
            output_file.write(augmented_string)


    #------------------------------------------------------------------------
    # Private below.

    @classmethod
    def _make_backup_of_existing_file(cls, original_file_path):
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
        shutil.copyfile(original_file_path, archive_fname)
        return dir_for_archive_copy, archive_fname

    @classmethod
    def _add_backup_location_comment(cls, backup_folder, one_big_string):
        comment_string = """
            # This file has been automatically re-formatted.
            # Previous versions can be found here:
            # %s
            ##
        """ % backup_folder
        comment_string = MultilineString.normalise(comment_string)
        if cls._BACKUP_COMMENT_RE.search(one_big_string):
            one_big_string = cls._BACKUP_COMMENT_RE.sub(
                    comment_string, one_big_string, 1)
        else:
            one_big_string = comment_string + '\n'+ one_big_string
        return one_big_string

    # Note the DOTALL in the regex. It means that the dot metacharacter
    # will define 'any character' to include newline - which it does not
    # by default.
    _BACKUP_COMMENT_RE = re.compile(r'# This file.*##', re.DOTALL)
