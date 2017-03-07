

class LayoutsMade(object):
    """
    Makes the layout hierarchy trees being called for by the records passed to the
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
        # First pass through the records, creates the QObjects called for by the left hand
        # side of each record, and registers them against their name.
        if __name__ == '__main__':
            for record in records:
                q_obj, err = self._create_parent_qobj(record)
                if err:
                    return None, err.extended_with('Failed to create parent QObject.')
                # Protest if the name is already in use.
                if record.parent_name in self.layouts:
                    clashing_record = self.layouts[record.parent_name]
                    return None, BuildError(
                        ('You cannot create a QObject called <%s> here: <%s>,' + \
                        'because there is already one of the same name created here: <%s>') %
                        (record.parent_name, record.file_location, clashing_record.file_location))
                # Otherwise register the new QObject.
                self.layouts[record.parent_name] = q_obj

            # Now we can assume that all the child references should resolve to something we have already
            # created. So the second pass adds the children to the parent objects
            for record in records:
                for child_name in record.child_name_fields:
                    child_qobj, err = self._find_child(child_name)
                    if err:
                        return err.extended_with('Failed to reconcile child name: <%s>, defined here: <%s>' %
                                                 (child_name, record.file_location))
                    # register the child
                    deploy reusable register if not in use print_function

                    # now add this child to the parent
                    foo
