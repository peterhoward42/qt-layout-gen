from PySide.QtGui import QLayout, QWidget

from objectfinder import ObjectFinder


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
        :param particular_class: The specific class you want to find
        instances of. E.g. MyAmazingLayoutClass
        :param reference_name: The required variable or attribute name.
        :return: A sequence of matching objects.
        """

        # First find all the QLayouts and QWidgets that are referenced by
        # that name.
        found_objects = self._object_finder.find_objects(reference_name)

        # Now reduce to only those of the specified particular class.
        filtered = [obj for obj in found_objects if
                    isinstance(obj, particular_class)]

        return filtered