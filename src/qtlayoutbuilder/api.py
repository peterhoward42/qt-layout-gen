from collections import OrderedDict

def build_from_file(file_path, write_file_back_out=False):
    lines = get_lines_from_file(file_path)
    builder = Builder(lines, write_file_back_out,
            provenance='file: %s' % file_path)
    return builder.build()

def build_from_multiline_string(multiline_string, write_file_back_out=False):
    lines = multiline_string.split('\n')
    builder = Builder(lines, write_file_back_out,
            provenance='multi-line ' 'string')
    return builder.build()

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

class LayoutError(Exception):

    def __init__(self, message):
        super(Exception, self).__init__(message)
