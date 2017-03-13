import gc

class ObjectFinder(object):
    """
    This class helps you find an object that is already instantiated in your
    program - by searching for the name you assigned it to when you
    instantiated it.

    For example, if anywhere in your program you have said:

        my_label = QLabel(), or
        some_thing.my_label = QLabel()

    You can find the QLabel object by specifying like this:

        find_objects('my_label')

    The search namespace is not as large as it seems on first sight. Please
    refer to this class' constructor.
    """

    def __init__(self, class_filters):
        """
        You are obliged to specify the classes of object the search should be
        limited to. This helps performance by reducing the search
        space, and allows the first 3 levels in a 5-deep nested loop to be run
        just once - i.e. at construction time.
        :param class_filters: A list of classes. E.g. (QWidget, QLayout)
        """
        if len(class_filters) == 0:
            raise RuntimeError('You must provide at least one class')
        self._available_objects = self._assemble_available_objects(
            class_filters)

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
                self._is_referenced_by_name(obj, reference_name)]

    #-------------------------------------------------------------------------
    # Private below
    #-------------------------------------------------------------------------

    def _assemble_available_objects(self, class_filters):
        """
        Provides a list of all objects known to the garbage collector that
        belong to the classes cited. (Or their subclasses).
        :param class_filters: The classes you wish to qualify.
        (QWidget, QLayout).
        :return: A sequence of objects.
        """
        all = self._get_all_objects()
        filtered = [obj for obj in all if \
                    self._belongs_to_one_of_these_classes(obj, class_filters)]
        return filtered

    def _get_all_objects(self):
        """
        Provides a sequence of all the objects being tracked by the garbage
        collector at this time.
        :return: The objects.
        """
        gc.collect() # Refreshes
        first_tier_objs = gc.get_objects()# These are always container objects.

        # Now add in the objects referred to inside the containers.
        all_objects_by_id = {} # Avoid duplicates.
        for first_tier_obj in first_tier_objs:
            obj_id = id(first_tier_obj)
            all_objects_by_id[obj_id] = first_tier_obj
            self._add_second_tier_objects(first_tier_obj, all_objects_by_id)
        return all_objects_by_id.values()

    def _add_second_tier_objects(self, first_tier_obj, all_objects_by_id):
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

    def _filtered_on_class(self, objects, class_filters):
        """
        Returns a copy of the list of objects provided, from which have
        been removed, all objects that do not belong to one of the classes
        cited by the class filters. (Or their subclasses).
        :param objects: Input objects.
        :param class_filters: Qualifying classes.
        :return: Output objects.
        """
        return [obj for obj in objects if
                self._belongs_to_one_of_these_classes(obj, class_filters)]

    def _belongs_to_one_of_these_classes(self, obj, classes):
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

    def _is_referenced_by_name(self, obj, name):
        """
        Does a reference exist in the program that has the given name, and that
        points to the given object of interest?
        :param obj: The object of interest.
        :param name: The name the reference must have.
        :return: Boolean.
        """
        referrers = gc.get_referrers(obj)

        # Is there a local variable called <name> that refers to the object?
        # We answer by looking at referrers to the object that are of type
        # frame.
        if self._is_referenced_by_a_stack_frame_name(referrers, obj, name):
            return True
        return False

    def _is_referenced_by_a_stack_frame_name(self, referrers, obj, name):
        """
        Is there a reference among the given referrers, that is a stack frame,
        which contains a local variable of the given name, which points to
        the object of interest?
        :param referrers: The references to scan.
        :param obj: The object of interest.
        :param name: The name the reference must have.
        :return: Boolean.
        """
        frame_referrers = [ref for ref in referrers if self._is_a_frame(ref)]
        for frame in frame_referrers:
            if name in frame.f_locals:
                object_referred_to = frame.f_locals[name]
                if object_referred_to == obj:
                    return True
        return False

    def _is_a_frame(self, obj):
        """
        Does the given object have the type 'frame'?
        :param obj: The object of interest.
        :return: Boolean.
        """
        return  obj.__class__.__name__ == 'frame'
