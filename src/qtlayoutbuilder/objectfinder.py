import gc


class ObjectFinder(object):
    """
    Provides a runtime query to find objects that are already instantiated
    somewhere in your program. You could specify 'QLabel' and 'my_label', and
    it will find the objects that belong to the class QLabel, and which
    furthermore are referenced by a local variable or attribute
    called 'my_label'. The results will include subclasses of QLabel too.

    The search for objects of the qualifying classes is relatively expensive,
    but is done at construction time only. The find_objects() query method then
    has a relatively small search space is is inexpensive.
    """

    def __init__(self, class_filters):
        """
        :param class_filters: The list of classes (class objects) you wish
        to search for instances of. E.g. (QWidget, QLabel).
        """
        if len(class_filters) == 0:
            raise RuntimeError('You must provide at least one class')
        self._available_objects = _assemble_available_objects(class_filters)

    def find_objects(self, reference_name):
        """
        The main API search function. See example in class doc string.

        Finds the objects that were instantiated at the time the constructor
        was called, and which passed the constructor's class filter criteria,
        and which are referenced (somewhere in your program) by a variable
        (or attribute) name of the name you have specified.
        :param reference_name: Name of variable or attribute to search for.
        :return: A list of objects that satisfy the search.
        """
        return [obj for obj in self._available_objects if
                _is_referenced_by_name(obj, reference_name)]

        # -------------------------------------------------------------------------
        # Private below
        # -------------------------------------------------------------------------


def _filtered_on_class(objects, class_filters):
    """
    Returns a copy of the list of objects provided, from which have
    been removed, all objects that do not belong to one of the classes
    cited by the class filters. (Or their subclasses).
    :param objects: Input objects.
    :param class_filters: Qualifying classes.
    :return: Output objects.
    """
    return [obj for obj in objects if
            _belongs_to_one_of_these_classes(obj, class_filters)]


def _is_referenced_by_name(obj, name):
    """
    Does a reference exist in the program that has the given name, and that
    points to the given object of interest?
    :param obj: The object of interest.
    :param name: The name the reference must have.
    :return: Boolean.
    """
    referrers = gc.get_referrers(obj)

    # Look for a qualifying reference among referrers to the object that
    # are stack frames. This will catch references that are local
    # variables or function arguments.
    if _is_referenced_by_a_stack_frame_name(referrers, obj, name):
        return True

    # Look for a qualifying reference among referrers to the object that
    # are dictionaries. This will catch references that are attributes
    # of an instantiated class.
    if _is_referenced_by_a_dict(referrers, obj, name):
        return True
    return False


def _assemble_available_objects(class_filters):
    """
    Provides a list of all objects known to the garbage collector that
    belong to the classes cited. (Or their subclasses).
    :param class_filters: The classes you wish to qualify.
    (QWidget, QLayout).
    :return: A sequence of objects.
    """
    all_objects = _get_all_objects()
    filtered = [obj for obj in all_objects if
                _belongs_to_one_of_these_classes(obj, class_filters)]
    return filtered


def _get_all_objects():
    """
    Provides a sequence of all the objects being tracked by the garbage
    collector at this time.
    :return: The objects.
    """
    gc.collect()  # Refresh
    first_tier_objs = gc.get_objects()  # These are always container objects.

    # Now add in the objects referred to inside the containers.
    all_objects_by_id = {}  # Avoid duplicates.
    for first_tier_obj in first_tier_objs:
        obj_id = id(first_tier_obj)
        all_objects_by_id[obj_id] = first_tier_obj
        _add_second_tier_objects(first_tier_obj, all_objects_by_id)
    return all_objects_by_id.values()


def _add_second_tier_objects(first_tier_obj, all_objects_by_id):
    """
    Augments the all_objects_by_id dictionary provided, with entries for
    the objects referred to by the given first tier object.
    :param first_tier_obj:
    :param all_objects_by_id: The dictionary to update.
    :return:
    """
    second_tier_objs = gc.get_referents(first_tier_obj)
    for second_tier_obj in second_tier_objs:
        obj_id = id(second_tier_obj)
        all_objects_by_id[obj_id] = second_tier_obj


def _belongs_to_one_of_these_classes(obj, classes):
    """
    Returns true if the given object belongs to one of the classes cited
    in the list of classes provided.
    :param obj: The object to test.
    :param classes: The qualifying classes.
    :return: Boolean.
    """
    for cls in classes:
        if isinstance(obj, cls):
            return True
    return False


def _is_referenced_by_a_stack_frame_name(referrers, obj, name):
    """
    Is there a reference among the given referrers, that is a stack frame,
    which contains a local variable of the given name, which points to
    the object of interest?
    :param referrers: The references to scan.
    :param obj: The object of interest.
    :param name: The name the reference must have.
    :return: Boolean.
    """
    frame_referrers = [ref for ref in referrers if _is_a_(ref, 'frame')]
    for frame in frame_referrers:
        if name in frame.f_locals:
            object_referred_to = frame.f_locals[name]
            if object_referred_to == obj:
                return True
    return False


def _is_referenced_by_a_dict(referrers, obj, name):
    """
    Is there a reference among the given referrers, that is a dict,
    which contains a key which is the given name, which points to
    the object of interest?
    :param referrers: The references to scan.
    :param obj: The object of interest.
    :param name: The name the reference must have.
    :return: Boolean.
    """
    dict_referrers = [ref for ref in referrers if _is_a_(ref, 'dict')]
    for _dict in dict_referrers:
        value = _dict.get(name, None)
        if value == obj:
            return True
    return False


def _is_a_(obj, class_name):
    return obj.__class__.__name__ == class_name
