from collections import OrderedDict

from PySide.QtGui import QWidget

from qtlayoutbuilder.api.layouterror import LayoutError


class LayoutsCreated(object):

    def __init__(self):
        # Access the items created like this: elements['my_page.right_btn']
        # (A level-two item)
        self._elements = OrderedDict()

    def get_element(self, path):
        element = self._elements.get(path, None)
        if element is None:
            raise LayoutError("""
                The path you have requested (<%s>) in get_element()
                does not exist in the layouts created.

                The paths that do exist are these:
                %s
            """, (path, self.dump()))
        return element

    def register_top_level_object(self, object, name):
        if name in self._elements:
            raise LayoutError("""
                The top-level name you have given this item (<%s>), has already
                been used.
            """, name)
        self._elements[name] = object

    def register_child(self, child_object, parent_path, child_name):
        key = parent_path + '.' + child_name
        if key in self._elements:
            raise LayoutError("""
                Each child you create for an object must have a unique name.
                You are duplicating the child name in this path (<%s>).
            """, key)
        self._elements[key] = child_object

    def most_recently_added_at_level(self, level):
        for key in reversed(self._elements.keys()):
            if len(key.split('.')) == level:
                return self._elements[key], key
        return None

    def current_level(self):
        keys = self._elements.keys()
        if len(keys) == 0:
            return 1
        last_key = self._elements.keys().pop()
        return len(last_key.split('.'))

    def is_empty(self):
        return len(self._elements.keys()) == 0

    def dump(self):
        key_lengths = [len(key) for key in self._elements.keys()]
        pad_columns = max(key_lengths) + 4
        lines = []
        for key, obj in self._elements.items():
            line = key.ljust(pad_columns) + obj.__class__.__name__
            lines.append(line)
        return '\n'.join(lines)

