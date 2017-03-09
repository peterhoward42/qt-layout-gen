""" Module defines the class DirectorySearch. """

import os

from layouterror import LayoutError


def find_all_files(path):
    """
    Returns a list of all the files found (recursively) in the given path.
    :param path: The directory path to start the search.
    :return: List of file names (paths)
    :raises LayoutError
    """
    file_list = []
    try:
        walk_results = os.walk(path, topdown=True, onerror=_handle_walk_error)
        for (dir_path, dir_names, file_names) in walk_results:
            for file_name in file_names:
                file_list.append(os.path.join(dir_path, file_name))
    except Exception as e:
        raise LayoutError(str(e), None)
    if len(file_list) == 0:
        raise LayoutError('No files found in %s' % path, None)
    return file_list





def _handle_walk_error(e):
    raise e

