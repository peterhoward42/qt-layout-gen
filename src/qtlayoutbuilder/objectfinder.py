import gc
from collections import defaultdict

from PySide.QtGui import QWidget, QLayout

def find_qobject_instances(class_name, reference_name):
    objects = _get_all_objects_that_have_an_id()
    objects = _reduce_to_qwidgets_or_qlayouts(objects)
    objects = _reduce_to_those_referenced_by_given_name(objects, reference_name)
    return objects

def _get_all_objects_that_have_an_id():
    # we only harvest those with id so that we can detect duplicates thus.
    gc.collect()
    first_tier_objs = gc.get_objects()
    all_objects_by_id = {}
    for first_tier_obj in first_tier_objs:
        obj_id = id(first_tier_obj)
        if obj_id is not None:
            all_objects_by_id[obj_id] = first_tier_obj
        _add_second_tier_objects(first_tier_obj, all_objects_by_id)
    return all_objects_by_id.values()

def _add_second_tier_objects(first_tier_obj, all_objects_by_id):
    second_tier_objs = gc.get_referents(first_tier_obj)
    for second_tier_obj in second_tier_objs:
        obj_id = id(second_tier_obj)
        if obj_id is None:
            continue
        all_objects_by_id[obj_id] = second_tier_obj

def _reduce_to_qwidgets_or_qlayouts(objects):
    return [obj for obj in objects if _is_qtype(obj, [QWidget, QLayout])]

def _is_qtype(obj, qtypes):
    for qtype in qtypes:
        if isinstance(obj, qtype):
            return True
    return False

def _reduce_to_those_referenced_by_given_name(objects, name):
    return [obj for obj in objects if _is_referenced_by_name(obj, name)]

def _is_referenced_by_name(obj, name):
    referrers = gc.get_referrers(obj)
    names = _names_of(referrers)
    return name in names

def _names_of(objects):
    names = [_get_name_of(obj) for obj in objects]
    names = [name for name in names if name is not None]
    return names

def _get_name_of(obj):
    name = getattr(obj, '__name__', None)
    return name




# say in comments - hit in constructor
