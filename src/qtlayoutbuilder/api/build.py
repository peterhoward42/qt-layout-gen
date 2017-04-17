from qtlayoutbuilder.lib import file_utils
from qtlayoutbuilder.lib.builder import Builder

tidy_and_overwrite=True

def build_from_file(file_path, tidy_and_overwrite):
    one_big_string = file_utils.get_file_contents_as_a_string(
            file_path)
    return Builder.build(
            one_big_string, file_path, tidy_and_overwrite)

def build_from_multi_line_string(one_big_string):
    return Builder.build(
            one_big_string, provenance='Multi-line string provided.')

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
