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
        First of all, populates self.layouts by creating the QObjects required by the LHS of
        each input record. Then, makes sure the children of each input text record can be resolved to
        the QObjects registered in the first pass, and augments self.layouts with these name-to-object
        look ups.
        :param records: The InputTextRecords from which the layouts should be made.
        :return: BuildError, or None
        """

        # First pass through the records, creates the QObjects called for by the left hand
        # side of each record, and registers each one against their name.
        for record in records:
            q_obj, parent_name, err =  _ParentMaker.make(record)
            if err:
                return None, err.extended_with('Failed to create parent QObject')
            err = self._register_if_no_clash(parent_name, record, q_obj)
            if err:
                return None, err.extended_with('Failed to create parent QObject.')

        # The second pass finds the (now created) QLayout or QWidget each child is referring to, and then,
        # having found it, adds adds it to its parent using addLayout() or addWidget(). Finally it adds an entry
        # to the register of layouts for the child name.
        for record in records:
            parent_name, err = _ParentMaker.isolate_parent_name(record)
            if err:
                return err.extended_with('Cannot isolate parent object name')
            parent_qobject = self.layouts[parent_name]
            if len(record.words) == 1: # There are no children
                return
            child_names = record.words[1:]
            for child_name in child_names:
                # Every child should refer to a QObject that is already registered.
                child_qobj = self.layouts.get(child_name, None)
                if child_qobj is None:
                    return BuildError(
                        'Failed to reconcile child name: <%s>, defined here: <%s>' %
                                (child_name, record.file_location))
                err = self._register_if_no_clash(child_name, record, child_qobj)
                if err:
                    return err.extended_with(('Failed to reconcile child name')
                err = self._add_child_to_parent(child_qobj, parent_qobject)
                if err:
                    return err.extended_with(('Problem adding this child name: <%s>' + \
                            'which is defined here: <%s>, to its parent')) % (child_name, record.file_location)

    def _register_if_no_clash(self, name, record, q_obj):
        """
        Registers the given object in self.layouts, unless there is already something
        registered with that name, in which case it returns a BuildError.
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
