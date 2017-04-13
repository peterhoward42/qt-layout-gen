from qtlayoutbuilder.api import LayoutError
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString


def raise_layout_error(multiline_format_string, arguments):
    format = MultilineString.shift_left(multiline_format_string)
    msg = format % arguments
    raise LayoutError(msg)

