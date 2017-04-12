

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
        pass

class LayoutError(Exception):

    def __init__(self, message):
        super(Exception, self).__init__(message)
