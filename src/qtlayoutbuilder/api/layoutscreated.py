class LayoutsCreated(object):
    """
    A container that holds all the nested QLayout(s) created. You can
    access the trees and constituent nodes produced by name in the
    'layout_elements' dictionary.
    """

    def __init__(self):
        # The layouts created are stored in the dictionaries below.
        # They are keyed on the names you used for parents and children in your
        # input text.

        # Every widget or layout the builder created is registered here.
        self.layout_element = {}

        # The file name and line number that provided the definition for every
        # element used is registered here.
        self.provenance = {} # Values are FileLocation(s)

