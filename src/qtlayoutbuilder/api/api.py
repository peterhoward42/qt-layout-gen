from qtlayoutbuilder.lib import inputsplitter
from qtlayoutbuilder.lib import builder

class LayoutBuilder(object):
    """
    This class produces nested QtLayouts on demand - based on a textual
    specification you provide. See the readme file for usage and scope.
    """

    @staticmethod
    def build_layouts_from_dir(dir):
        """
        Builds and returns a LayoutsCreated object based on the files found
        in the directory provided. The LayoutsCreated class is defined in a
        sister module.

        All the files in the given directory are consumed (recursively).

        :param input_directory_path: The directory to search.
        :return: A LayoutsCreated object.
        :raises: LayoutError (defined below)
        """

        records = inputsplitter.split_all_files_in_directory_into_records(dir)
        return builder.Builder(records).build()

    @staticmethod
    def build_layouts_from_text(one_big_string):
        """
        Builds and returns a LayoutsCreated object based on the input text
        provided. The LayoutsCreated class is defined in a sister module.

        :param one_big_string: Your textual specification.
        :return: A LayoutsCreated object.
        :raises: LayoutError (defined below)
        """
        records = inputsplitter.split_big_string_into_records(one_big_string)
        return builder.Builder(records).build()


