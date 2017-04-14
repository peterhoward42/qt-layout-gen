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

class LayoutsCreated(object):

    def __init__(self):
        # Access the items created like this: elements['my_page.right_btn']
        # (A level-two item)
        self.elements = OrderedDict()

    def register_top_level_object(self, object, name):
        key = name
        self.elements[key] = object

    def register_child(self, child_object, parent_path, child_name):
        key = parent_path + '.' + child_name
        self.elements[key] = child_object

    def most_recently_added_at_level(self, level):
        for key in reversed(self.elements.keys()):
            if len(key.split('.')) == level:
                return self.elements[key], key
        return None

class LayoutError(Exception):

    def __init__(self, message):
        super(Exception, self).__init__(message)
