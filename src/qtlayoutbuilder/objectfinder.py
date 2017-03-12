import gc
from collections import defaultdict

from PySide.QtGui import QWidget, QLayout

def find_qobject_instances(class_name, reference_name):
    gc.collect()
    objects = gc.get_objects()
    matching = []
    for obj in objects:
        class_name = _get_class_name_if_possible(obj)
        if class_name is None:
            continue
        if class_name.startswith('Q'):
            if class_name in  ['QMetaObject', 'Queue', 'Quitter', 'QApplication']:
                continue
        if not isinstance(obj, QWidget) and not isinstance(obj, QLayout):
            continue
        referrers = gc.get_referrers(obj)
        for referrer in referrers:
            if referrer.__name__ == reference_name:
                matching.append(object)
    return matching



class ObjectFinder(object):

    def __init__(self):
        self.objects_by_class = defaultdict(list)

        gc.collect()
        objects = gc.get_objects()
        for obj in objects:
            class_name = self._get_class_name_if_possible(obj)
            if class_name is None:
                continue
            self.objects_by_class[class_name].append(obj)

    def find(self, class_name, reference_name):
        # returns info hat contains the objects that satisfy the conditions,
        objects = self.objects_by_class.get(class_name, [])
        objects = self._filter_on_reference_names(objects, reference_name)
        return objects

    def _filter_on_reference_names(self, objects, reference_name):
        found = []
        for obj in objects:
            # beware our look up table will show up as a referrer.
            referrers = gc.get_referrers(obj)
            for referrer in referrers:
                # lists seem to be the happy hunting ground
                class_name = self._get_class_name_if_possible(referrer)
                """
                if class_name != 'list':
                    continue
                    """
                try:
                    if reference_name in referrer:
                        found.append(obj)
                        break # from referrer loop, we have a sufficient condition to return this outer loop obj, and don't want to double include it in the returned list
                except TypeError as e: # not iterable like frame
                    continue
        return found

    def _get_class_name_if_possible(self, obj):
        cls = getattr(obj, '__class__', None)
        if cls is None:
            return None
        name = getattr(cls, '__name__', None)
        if name is None:
            return None
        return name

def _get_class_name_if_possible(obj):
    cls = getattr(obj, '__class__', None)
    if cls is None:
        return None
    name = getattr(cls, '__name__', None)
    if name is None:
        return None
    return name


# say in comments - hit in constructor
