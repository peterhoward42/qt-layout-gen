from PyQt5.QtWidgets import QLayout, QWidget

from qtlayoutbuilder.lib.objectfinder import ObjectFinder


class WidgetAndLayoutFinder(object):
    """
    Provides a runtime query that can find QWidgets and QLayouts that
    are already instantiated in your program. You specify the ones you want
    to search for by specifying the particular layout or widget class the
    objects must be (which can include your derived classes). You also specify
    the name of the variable (or attribute) you assigned it to when you
    instantiated it.

    For example you can look for a QHBoxLayout you called 'my_layout'.

    This is a convenience wrapper around ObjectFinder, but also provides the
    ADDITIONAL filtering criteria - which is the particular class you want to
    find.

    Note that construction of this class is expensive, but subsequent searches
    with it are not.
    """

    def __init__(self):
        self._object_finder = ObjectFinder([QLayout, QWidget])

    def find(self, particular_class, reference_name):
        """
        The query function.
        :param particular_class: The NAME of the specific class you want to
        find instances of. E.g. 'MyAmazingLayoutClass', or 'QLabel'.
        :param reference_name: The required variable or attribute name. E.g.
        'my_amazing_layout'
        :return: A sequence of matching objects.
        """

        # First find all the QLayouts and QWidgets that are referenced by
        # that name.
        found = self._object_finder.find_objects(reference_name)

        # Now reduce to only those of the specified particular class.

        filtered = [obj for obj in found if
                    obj.__class__.__name__ == particular_class]

        return filtered
