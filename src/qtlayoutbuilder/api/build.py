from qtlayoutbuilder.lib import file_utils
from qtlayoutbuilder.lib.builder import Builder
from qtlayoutbuilder.lib.original_file_rewriter import OriginalFileReWriter
from qtlayoutbuilder.lib.reformatter import ReFormatter


def build_from_file(file_path, auto_format_and_overwrite=True):
    """
    Builds a QtLayout and QtWidget hierarchy based on the input text provided
    in the input file specified.
    :param file_path:  Full path of input file.
    :param auto_format_and_overwrite: Set this to False to prevent the builder
    from automatically reformatting and overwriting the input file.
    :raises LayoutError:
    :return: A LayoutsCreatedAccessor object.
    """
    one_big_string = file_utils.get_file_contents_as_a_string(file_path)
    layouts_created = Builder.build(one_big_string, file_path)
    if auto_format_and_overwrite:
        re_formatted = ReFormatter.format(one_big_string)
        OriginalFileReWriter.overwrite_original(file_path, re_formatted)
    return LayoutsCreatedAccessor(layouts_created)


def build_from_multi_line_string(one_big_string, auto_format_and_write_to=''):
    """
    Builds a QtLayout and QtWidget hierarchy based on the input text provided
    in the (multi-line) input string provided.
    :param one_big_string: The input text.
    :param auto_format_and_write_to: Set this to a non-empty file pathname to
    make the builder automatically reformat the input and write the formatted
    input to that file.
    :raises LayoutError:
    :return: A LayoutsCreatedAccessor object.
    """
    layouts_created = Builder.build(one_big_string, 'No input file used')
    if auto_format_and_write_to:
        re_formatted = ReFormatter.format(one_big_string)
        with open(auto_format_and_write_to, 'w') as output_file:
            output_file.write(re_formatted)
    return LayoutsCreatedAccessor(layouts_created)


class LayoutsCreatedAccessor(object):
    """
    A container for the layouts and widget hieararchies created by the builder.
    You query for any object in the built hierarchy using the at() method.
    """

    def __init__(self, layouts_created):
        # Provide a LayoutsCreated object.
        self._impl = layouts_created

    def at(self, name):
        """
        Find the item with the given name.
        :param name: The name to search for.
        :raises LayoutError:
        :return: The QLayout or QWidget at that position in the hierarchy.
        """
        return self._impl.at(name)

    def first_top_level_item(self):
        """
        Returns the first item in the build hierarchy. Created to support
        the tools/helper_gui - which cannot know what name to search for.
        """
        return self._impl.first_top_level_item()
