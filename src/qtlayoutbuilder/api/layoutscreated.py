
class LayoutsCreated(object):
    """
    A container that holds the nested QLayout(s) created produced. You can
    access the trees and constituent nodes produced by name in the
    'layout_elements' dictionary.

    Also offers some methods and attributes to support diagnostics.
    """

    def __init__(self):
        # The layouts created are stored in the dictionaries below.
        # They are keyed on the names you used for things in your input
        # text.

        # Every widget or layout the builder created is registered here.
        self.layout_element = {}

        # The file name and line number that provided the definition for every
        # element used.
        self.provenance = {} # Values are FileLocation(s)

