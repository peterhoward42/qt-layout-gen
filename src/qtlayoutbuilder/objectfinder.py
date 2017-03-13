import gc

class ObjectFinder(object):
    """
    This class helps you find objects that are already instantiated in your
    program. For example, if anywhere in your program you have said:

        my_label = QLabel(), or
        some_thing.my_label = QLabel()

    You can find the QLabel object instantiated by specifying the required
    class and the name by which you have referenced it. (Both strings).

        find_objects('QLabel', 'my_label').
    """

    def __init__(self, base_class_filters):
        """
        You are required to specify base class constraints to the constructor,
        like [QLayout, QWidget]. It helps performance by reducing the search
        space, and allows the first 3 levels in a 5-deep nested loop to be run
        just once - i.e. at construction time.
        :param base_class_filters: The base classes you stipulate.
        """
        if len(base_class_filters) == 0:
            raise RuntimeError('You must provide at least one base class')
        self._objects = self._assemble_available_objects(base_class_filters)

    def find_objects(self, class_name, reference_name):
        """
        Finds any objects that were instantiated when the constructor was
        called, that passed the constructor's base class filter criteria, and
        which are of the class you have specified in the <class_name> parameter,
        and which are referenced (somewhere in your program) by a variable
        (or attribute) name of the name you have specified.
        :param class_name: Class to search for.
        :param reference_name: Name of variable or attribute to search for.
        :return: A list of objects that qualify.
        """
        found = self._reduce_to_those_referenced_by_given_name(reference_name)
        return found

    def _assemble_available_objects(self, base_class_filters):
        objects = self._get_all_objects_that_have_an_id()
        objects = self._filtered_on_base_class(objects, base_class_filters)
        return objects

    def _get_all_objects_that_have_an_id(self):
        # we only harvest those with id so that we can detect duplicates thus.
        gc.collect()
        first_tier_objs = gc.get_objects()
        all_objects_by_id = {}
        for first_tier_obj in first_tier_objs:
            obj_id = id(first_tier_obj)
            if obj_id is not None:
                all_objects_by_id[obj_id] = first_tier_obj
            self._add_second_tier_objects(first_tier_obj, all_objects_by_id)
        return all_objects_by_id.values()

    def _add_second_tier_objects(self, first_tier_obj, all_objects_by_id):
        second_tier_objs = gc.get_referents(first_tier_obj)
        for second_tier_obj in second_tier_objs:
            obj_id = id(second_tier_obj)
            if obj_id is None:
                continue
            all_objects_by_id[obj_id] = second_tier_obj

    def _filtered_on_base_class(self, objects, base_class_filters):
        return [obj for obj in objects if self._is_correct_base_class(obj, base_class_filters)]

    def _is_correct_base_class(self, obj, qtypes):
        for qtype in qtypes:
            if isinstance(obj, qtype):
                return True
        return False

    def _reduce_to_those_referenced_by_given_name(self, name):
        return [obj for obj in self._objects if self._is_referenced_by_name(obj, name)]

    def _is_referenced_by_name(self, obj, name):
        referrers = gc.get_referrers(obj)
        # for local vars we look only in referrers that are frames
        frame_referrers = [ref for ref in referrers if self._is_a_frame(ref)]
        for frame in frame_referrers:
            if self._frame_has_local_var_of_this_name(frame, name):
                points_to = self._fetch_local(frame, name)
                if points_to == obj:
                    return True
        return False

    def _frame_has_local_var_of_this_name(self, frame, name):
        local_variable_names = frame.f_locals.keys()
        return name in local_variable_names

    def _fetch_local(self, frame, name):
        return frame.f_locals[name]

    def _is_a_frame(self, obj):
        cls = obj.__class__
        class_name = obj.__class__.__name__
        return class_name == 'frame'
