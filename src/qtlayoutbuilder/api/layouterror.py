from qtlayoutbuilder.lib.multiline_string_utils import MultilineString


class LayoutError(Exception):
    """
    The universal Exception raised by this package.
    """

    def __init__(self, multiline_format_string, args):
        str_format = MultilineString.normalise(multiline_format_string)
        message = str_format % args
        super(Exception, self).__init__(message)
