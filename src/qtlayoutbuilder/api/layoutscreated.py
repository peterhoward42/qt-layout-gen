
class LayoutsCreated(object):
    """
    A container that holds the nested QLayout(s) created produced. You can
    access the trees and constituent nodes produced by name in the
    'layout_elements' dictionary.

    Also offers some methods and attributes to support diagnostics.
    """

    def __init__(self):
        # Every QLayout/QWidget incorporated into a layout.
        self.layout_element_from_name = {}

        # Whereabouts in the input text each element was defined.
        # Values are FileLocation(s) - defined below.
        self.source_file_location_from_name = {}

