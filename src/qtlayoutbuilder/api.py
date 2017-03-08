"""
This module exposes the public API to the layout builder.
"""

from inputsplitter import _split_all_files_in_directory_into_records, _split_text_into_records
from layoutsmade import LayoutsMade

def build_layouts_from_dir(input_directory_path):
    """
    The API entry point to make layouts from files in a directory.
    All the files in the given directory are consumed (recursively).
    The function returns a LayoutsMade object when successful, or a BuildError
    otherwise.
    :param input_directory: The directly in which the layouts are defined.
    :return: (LayoutsMade, BuildError)
    """
    records, err = _split_all_files_in_directory_into_records(input_directory_path)
    if err:
        return None, err.extended_with('Could not build your layouts from <%s>' % input_directory)
    return LayoutsMade.make_from(records)

def build_layouts_from_text(input_text):
    """
    The API entry point to make layouts from text passed in as a parameter.
    The function returns a LayoutsMade object when successful, or a BuildError
    otherwise.
    :param input_text: The text in which the layouts are defined.
    :return: (LayoutsMade, BuildError)
    """
    records, err = _split_text_into_records(input_text)
    if err:
        return None, err.extended_with('Could not build your layouts from <%s>' % input_text)
    return LayoutsMade.make_from(records)


