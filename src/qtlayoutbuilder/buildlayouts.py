from builderror import BuildError

from keywords import instantiate_qobject_for


def _build_layouts_from_records(records, input_source_for_error_handling):
    """
    Builds the layout tree(s) comprising QLayouts and QWidgets, as mandated
    by the InputTextRecords provided.
    :param records: The text records from which the layout tree(s) should be produced.
    :param input_source_for_error_handling:
    :return: (layout_trees, BuildError). Where layout_trees is a dictionary keyed on the
    names used in the InputTextRecords.
    """
    layouts, err = _build_layouts_from_input_records(records)
    if err:
        return None, err.extended_with('Could not build your layouts from <%s>' % input_source_for_error_handling)

    # Algorithm:
    #
    # Our outer loop is to iterate over all the input text records building and
    # registering a QObject accordingly against its name. Each of these will be dependent on the
    # child objects cited by the record having already been resolved into child
    # QObjects themselves. We deal with this by recursively resolving the child objects first
    # when we encounter them. This means as we iterate through the input records we will routinely
    # encounter records that have been already built as a consequence of the recursion, in which case
    # we simply skip them.

    register = {}
    for record in records:
       err = _build_and_register_record(record, register)
    if err:
        return None, err.extended_with('Problem building one of your QObjects')

    # maybe should check nothing got left unconsumed here?


def _build_and_register_record(record, register):
    """
    Works out what q_objects are required to make the tree fragment implied by the
    given InputTextRecord, instantiating them (recursively) if necessary. Finally,
    registering the parent object from the input text record in the register
    provided.
    :param record: The InputTextRecord from which to build this sub tree.
    :param register: A dictionary that provides the previously registered
    q_objectes, keyed on their name. This method will update this dictionary
    as it goes. AND IS THE ONLY METHOD THAT SHOULD ADD TO THE register.
    :return: A BuildError or none.
    """
    # Already been done?
    parent_name = record.parent_name
    if parent_name in register:
        return None

    # Build and access children required
    children = {}
    for child_name in record.child_name_fields:
        q_object, err = _reconcile_child_to_object(child_name, record, register)
        if err:
            return err.extended_with(
                'Problem building child: <%s>, in record which is defined here: <%s>' %
                (child_name, record.file_location))
        children[parent_name] = q_object

    # Instantiate the relevant parent type and register it
    parent_qobject, err = instantiate_qobject_for(record.layout_keyword)
    if err:
        return err.extended_with(
            'Problem building <%s> for: record which is defined here: <%s>' %
            (parent_name, record.file_location))
    register[parent_name] = parent_qobject

    # Add the children to it
    for child_name, child_q_object in children.items():
        try:
            if isintance(child_q_object, QLayout):
                parent_qobject.addLayout(child_q_object)
            elif isintance(child_q_object, QWidget):
                parent_qobject.addWidget(child_q_object)
            else:
                raise Exception('Coding error, expected QWidget or QLayout and got <%s>' % child_q_object.__class__)
        except Exception as e:
            return BuildError(str(e)).extended_with(
                'Could not add child: <%s> to parent: <%s>, defined here: <%s>' %
                (child_name, parent_name, record.file_location))  # Return it
    return None


def _reconcile_child_to_object(child_name, record, register):
    """
    Will provide a q_object to reconcile the child_name given, using the
    InputTextRecord and register of previously registered QObjects as
    context.
    :param child_name: The name of the child that must be reconciled.
    :param record: The relevant InputTextRecord
    :param register: A dictionary that provides the previously registered
    q_objects, keyed on their name. This method DOES NOT update this dictionary
    as it goes of itself, but when it finds that the child name refers to another
    record, it will call _build_and_register_record() for that record recursively, -
    which will update the register as necessary.
    :return: (q_object, BuildError)
    """
    # Highest precedence is to find that a q_object is already
    # registered for the given child name.
    if child_name in register:
        return register[child_name], None

    # Temporarily regard everything else as an error
    return None, BuildError(
        ('Nothing found in register for this child name: <%s>, defined at: <%s>, ' + \
        'and no other machinery supported yet') % (child_name, record.file_location))
