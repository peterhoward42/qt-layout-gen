"""
This module exposes the public API to the Qt layout builder.
"""

from lib import inputsplitter
from lib import builder

class LayoutBuilder(object):
    """
    This class produces nested QtLayouts on demand - based on a textual
    specification you provide. See the readme file for usage and scope.
    """

    @staticmethod
    def build_layouts_from_dir(input_directory_path):
        """
        Builds and returns a LayoutsCreated object based on the files found
        in the directory provided. The LayoutsCreated class is defined below.

        All the files in the given directory are consumed (recursively).

        :param input_directory_path: The directory to search.
        :return: A LayoutsCreated object.
        :raises: LayoutError (defined below)
        """

        records = inputsplitter._split_all_files_in_directory_into_records('sillydirname')
        return builder.Builder(records).build()

    @staticmethod
    def build_layouts_from_text(one_big_string):
        """
        Builds and returns a LayoutsCreated object based on the input text
        provided. The LayoutsCreated class is defined below.

        :param one_big_string: Your textual specification.
        :return: A LayoutsCreated object.
        :raises: LayoutError (defined below)
        """
        records = inputsplitter._split_big_string_into_records(one_big_string)
        return builder.Builder(records).build()

class LayoutsCreated(object):
    """
    A container that holds the nested QLayout(s) created produced. You can
    access the trees and constituent nodes produced by name in the
    'layout_elements' dictionary.

    Also offers some methods and attributes to support diagnostics.
    """

    def __init__(self):
        # Every QLayout/QWidget incorporated into a layout.
        self.layout_element_from_name = {}

        # Whereabouts in the input text each element was defined.
        # Values are FileLocation(s) - defined below.
        self.source_file_location_from_name = {}


class LayoutError(Exception):
    """
    The one and only Exception type thrown from this package. The default
    string representation is a comprehensive user-facing message, which
    includes the input file name and line number that caused the problem.
    """

    def __init__(self, message, file_location):
        """
        Code that raises this exception should pass in a human-friendly
        string message and a FileLocation object to carry information about
        which bit of the input text caused the error.
        :param message: The message.
        :param file_location:  The FileLocation object.
        """
        super(Exception, self).__init__(message)
        self._file_location = file_location

    def __str__(self):
        return self.message + ', (%s)' % self._file_location

class FileLocation(object):
    """
    A simple container to hold the name of a file and a line number with it.
    """

    def __init__(self, file_name, line_number):
        self.file_name = file_name
        self.line_number = line_number

    def __str__(self):
        return '%s, at line %d' % (self.file_name, self.line_number)
