from qtlayoutbuilder.lib.multiline_string_utils import MultilineString


class LayoutError(Exception):

    def __init__(self, multiline_format_string, args):
        format = MultilineString.normalise(multiline_format_string)
        message = format % args
        super(Exception, self).__init__(message)
