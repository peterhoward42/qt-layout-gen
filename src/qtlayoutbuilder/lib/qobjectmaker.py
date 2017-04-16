from PySide.QtGui import * # So that we can construct any QObject from a string.

from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib.qtclassnameprompter import QtClassNamePrompter


class QObjectMaker(object):
    def __init__(self, widget_and_layout_finder):
        self._widget_and_layout_finder = widget_and_layout_finder

    def make(self, name, type_word):
        if type_word.startswith('?'):
            return self._find_existing_object(name, type_word[1:])
        else:
            return self._instantiate_object(type_word)

    # ----------------------------------------------------------------------------
    # Private below

    def _instantiate_object(self, type_word):
        """
        Instantiates a QObject of the type specified by the name.
        """
        constructor = None
        try:
            constructor = globals()[type_word]
        except KeyError as e:
            raise LayoutError("""
                Python cannot find this word in the QtGui namespace: <%s>,
                Did you mean one of these:

                %s
            """, (type_word, self._generate_name_suggestions(type_word)))

        # Have a go at constructing it, and then make sure it is a class derived
        # from QLayout or QWidget.
        try:
            instance = constructor()
        except Exception as e:
            raise LayoutError("""
                    Cannot instantiate one of these: <%s>.
                    It is supposed to be the name a a QLayout or QWidget
                    class, that can be used as a constructor.
                    The error coming back from Python is:
                    %s.
            """, (type_word, str(e)))

        # Make sure it is a QWidget or QLayout
        if isinstance(instance, QWidget):
            return instance
        if isinstance(instance, QLayout):
            return instance
        raise LayoutError("""
            This class name: <%s>, instantiates successfully,
            but is neither a QLayout nor a QWidget.
        """, (type_word))

    def _find_existing_object(self, name, type_word):
        """
        Tries to find an already-instantiated QWidget or QLayout that is of
        the class specified by the type_word provided, and which is
        referenced by a
        variable or attribute having the name specified by the name provided.
        """

        found = self._widget_and_layout_finder.find(type_word, name)

        # Object to nothing found, or duplicates found.
        if len(found) == 0:
            raise LayoutError("""
                Cannot find any objects of class <%s>,
                that are referenced by a variable or attribute
                called <%s>
            """, (type_word, name))
        if len(found) > 1:
            raise LayoutError("""
                Ambiguity problem. Found more than one object of
                class: <%s>, referenced by a variable or attribute
                called: <%s>
            """, (type_word, name))

        # All is well
        return found[0]

    def _generate_name_suggestions(self, duff_word):
        list_of_names = QtClassNamePrompter.suggest_names_similar_to_this(
                duff_word)
        return '\n'.join(list_of_names)

