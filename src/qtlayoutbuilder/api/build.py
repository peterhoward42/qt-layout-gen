from qtlayoutbuilder.lib import file_utils
from qtlayoutbuilder.lib.reformatter import ReFormatter
from qtlayoutbuilder.lib.builder import Builder
from qtlayoutbuilder.lib.original_file_rewriter import OriginalFileReWriter


def build_from_file(file_path, auto_format=True):
    one_big_string = file_utils.get_file_contents_as_a_string(
            file_path)
    layouts_created = Builder.build(one_big_string, file_path)
    if auto_format:
        re_formatted = ReFormatter.format(one_big_string)
        OriginalFileReWriter.overwrite_original(file_path, re_formatted)
    return LayoutsCreatedAccessor(layouts_created)

def build_from_multi_line_string(one_big_string, auto_format=True):
    layouts_created = Builder.build(one_big_string, 'No input file used')
    if auto_format:
        re_formatted = ReFormatter.format(one_big_string)
        ClipBoardWriter.write(re_formatted)
    return LayoutsCreatedAccessor(layouts_created)

class LayoutsCreatedAccessor(object):

    def __init__(self, layouts_created):
        # Provide a LayoutsCreated object.
        self._impl = layouts_created

    def get_element(self, path):
        # Access the items created like this: elements['my_page.right_btn']
        # (A level-two item)
        return self._impl.get_element(path)

    def dump(self):
        return self._impl.dump()
