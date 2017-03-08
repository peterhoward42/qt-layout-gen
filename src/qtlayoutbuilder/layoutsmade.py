from qobjectmaker import _create_parent_qobj
from builderror import BuildError

class LayoutsMade(object):
    """
    Makes the layout hierarchy trees as described by the records passed to the
    the make_from() method. Exposes them for the client, post-build, in self.layouts.
    """

    def __init__(self):
        self.layouts = {} # Keyed on the names you use in the input text records

    @classmethod
    def make_from(cls, records):
        """
        A factory that makes a LayoutsMade object, populates it by running the
        build process and then returns the LayoutsMade object.
        :param records: The InputTextRecords from which the layouts should be made.
        :return: (LayoutsMade, BuildError). # One will be non-null.
        """
        layouts_made = LayoutsMade()
        err = layouts_made._build(records)
        if err:
            return None, err.extended_with('Failed to build layout.')
        return layouts_made, None

    def _build(self, records):
        """
        First of all, populates self.layouts by creating the QObjects required for the parent of
        each input record. Then, makes sure the children of each input text record can be resolved to
        the QObjects registered in the first pass, and augments self.layouts with these name-to-object
        look ups.
        :param records: The InputTextRecords from which the layouts should be made.
        :return: BuildError, or None
        """

        # First pass through the records, creates the QObjects called for by the left hand
        # side of each record, and registers each one against their name.
        for record in records:
            q_obj, err = _create_parent_qobj(record)
            if err:
                return None, err.extended_with('Failed to create parent QObject.')
            err = self._register_if_no_clash(record.parent_name, record, q_obj)
            if err:
                return err

        # Second pass resolves the children, and adds them to their parent objects
        for record in records:
            for child_name in record.child_name_fields:
                # Every child should refer to a QObject that is already registered.
                child_qobj = self.layouts.get(child_name, None)
                if child_qobj is None:
                    return BuildError(
                        'Failed to reconcile child name: <%s>, defined here: <%s>' %
                                (child_name, record.file_location))
                err = self._register_if_no_clash(record.parent_name, record, q_obj)
                if err:
                    return err.extended_with(('Problem resolving this child name: <%s>' + \
                            'which is defined here: <%s>')) % (child_name, record.file_location)
                err = self._add_child_to_parent(child_qobj, self.layouts[record.parent_name])
                if err:
                    return err.extended_with(('Problem adding this child name: <%s>' + \
                            'which is defined here: <%s>, to its parent')) % (child_name, record.file_location)

    def _register_if_no_clash(self, name, record, q_obj):
        """
        Registers the given object in the self.layouts, unless there is already something
        registered with that name, in which case it returns a non-None error.
        :param name: The name the object should be registered to.
        :param q_obj: The object to register.
        :return: BuildError or None
        """
        if name in self.layouts:
            clashing_record = self.layouts[name]
            return BuildError(
                ('You cannot create a QObject called <%s> here: <%s>,' + \
                 'because there is already one of the same name created here: <%s>') %
                (name, record.file_location, clashing_record.file_location))
        # Otherwise register the new QObject.
        self.layouts[name] = q_obj
