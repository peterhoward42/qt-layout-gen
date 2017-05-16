from collections import OrderedDict

from qtlayoutbuilder.api.layouterror import LayoutError


class LayoutsCreated(object):
    def __init__(self):
        # Access the items created like this: elements['my_page.right_btn']
        # (A level-two item)
        self._elements = OrderedDict()

    def at(self, name):
        """
        Find the item with the given name.

        :param name: The name to search for.
        :raises LayoutError:
        :return: The QLayout or QWidget at that position in the hierarchy.
        """
        matching_paths = [path for path in self._elements.keys() if
                          self._name_segment(path) == name]
        if len(matching_paths) == 0:
            raise LayoutError("""
                No path can be found that ends with <%s>.
                These are the paths that do exist:

                %s
            """, (name, self.dump()))
        if len(matching_paths) > 1:
            raise LayoutError("""
                More than one path exists that ends with <%s>.

                The first two are:
                %s
                %s
            """, (name, matching_paths.pop(), matching_paths.pop()))
        return self._elements[matching_paths.pop()]

    def register_top_level_object(self, object_to_register, name):
        if name in self._all_names():
            raise LayoutError("""
                The name you have given this item (<%s>), has already
                been used.
            """, name)
        self._elements[name] = object_to_register

    def register_child(self, child_object, parent_path, child_name):
        if child_name in self._all_names():
            raise LayoutError("""
                The name you have given this item (<%s>), has already
                been used.
            """, child_name)
        key = parent_path + '.' + child_name
        self._elements[key] = child_object

    def first_top_level_item(self):
        if len(self._elements.keys()) == 0:
            return None
        key = self._elements.keys()[0]
        return self._elements[key]

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

    # ------------------------------------------------------------------------
    # Private below

    def _all_names(self):
        names = [self._name_segment(path) for path in self._elements.keys()]
        return names

    def _name_segment(self, path):
        return path.split('.').pop()
