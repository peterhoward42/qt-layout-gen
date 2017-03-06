""" Module defines the class DirectorySearch. """

import os

from builderror import BuildError


def find_all_files(path):
    """
    Returns a list of all the files found (recursively) in the given path, or
    provides a non-None BuildError describing something having gone wrong.
    :param path: The directory path to start the search.
    :return: (files, err).
    """
    try:
        walk_results = os.walk(path, topdown=True, onerror=_handle_walk_error)
        file_list = []
        for (dir_path, dir_names, file_names) in walk_results:
            for file_name in file_names:
                file_list.append(os.path.join(dir_path, file_name))
        if len(file_list) == 0:
            return None, BuildError('No files found in %s' % path)
        return file_list, None
    except Exception as e:
        err = BuildError(str(e))
        return None, err.extended_with('Problem in find_all_files for your path: <%s>' % path)


def _handle_walk_error(e):
    raise e

