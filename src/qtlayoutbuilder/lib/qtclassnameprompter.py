import difflib

from PyQt5 import QtWidgets


class QtClassNamePrompter(object):
    """
    Capable of providing a list of similar looking Qt class names to the
    one you provide.
    """

    @classmethod
    def suggest_names_similar_to_this(cls, name):
        all_qtgui_names = dir(QtWidgets)
        lower_cased = [n.lower() for n in all_qtgui_names]
        # The search is done in lower-case space, so we need a map to return
        # the results to their original case.
        lowercase_to_original_map = {}
        for orig, lowered in zip(all_qtgui_names, lower_cased):
            lowercase_to_original_map[lowered] = orig
        similar_names = difflib.get_close_matches(name.lower(), lower_cased,
                                                  cls._LIMIT, cutoff=0.0)
        result = [lowercase_to_original_map[similar_name] for similar_name in
                  similar_names]
        return result

    # -------------------------------------------------------------------------
    # Private below.

    _LIMIT = 6
