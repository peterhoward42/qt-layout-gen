"""
This module defines the Builder class.
"""

from PySide.QtGui import QBoxLayout

from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.api.layoutscreated import LayoutsCreated
from widgetandlayoutfinder import WidgetAndLayoutFinder
from qtlayoutbuilder.lib.childadder import ChildAdder
import qobjectmaker_orig


class BuilderOld(object):
    """
    This class produces nested QtLayouts on demand - based a sequence of
    prepared InputTextRecords. See the API module for more details of what
    is produced.
    """

    def __init__(self, records):
        """
        The Builder is bound for its life to the InputTextRecords provided at
        construction time. (Avoids re-init code and reduces bug surface).
        :param records: The InputTextRecords to use.
        """
        self._records = records

    def build(self):
        """
        Builds and returns a LayoutsCreated object populated with the layout
        hierarchies specified in the records provided.
        :return: LayoutsCreated.
        """

        layouts_created = LayoutsCreated()

        # First we create and register all the parent objects, because these
        # provide the objects that child names (usually) must refer to.
        self._create_and_register_parent_objects(layouts_created)

        # Now we can process the children.
        for record in self._records:
            parent_qobject = layouts_created.layout_element[
                record.parent_name]
            self._process_children(parent_qobject, record, layouts_created)

        return layouts_created

    # -------------------------------------------------------------------------
    # Private below

    def _create_and_register_parent_objects(self, layouts_created):
        """
        Iterates over all the InputTextRecords provided and makes the parent
        QObject mandated by the record and registers them by name in the
        LayoutsCreated provided. Raises LayoutException if the parent name
        is already registered, or if the object is already registered. The
        latter can arise in the case of the record asking for an existing
        QObject to be found, rather than minting a new one.
        :param layouts_created: The LayoutsCreated to register things with.
        :return: None
        :raises: LayoutError
        """
        finder = WidgetAndLayoutFinder()  # Expensive construction!
        for record in self._records:
            # Make the qobject.
            parent_qobject, parent_name = qobjectmaker_orig.make_from_parent_info(
                record, finder)
            # And then register it.
            self._register(parent_name, parent_qobject, record, layouts_created)

    @staticmethod
    def _assert_name_not_already_taken(name, record, layouts_created):
        # Raises a LayoutError if the name provided is found to be already
        # registered in the LayoutsCreated object provided.
        if name not in layouts_created.layout_element:
            return
        prior_use = layouts_created.provenance[name]
        raise LayoutError(
            '\n'.join([
                'You cannot use this name: <%s> again, because it',
                'has already been used here: <%s>'
            ]) %
            (name, prior_use), record.file_location)

    def _register(self, name, qobject, record, layouts_created):
        # Registers the given QObject against the given name in the
        # LayoutsCreated object provided.
        self._assert_name_not_already_taken(name, record, layouts_created)
        layouts_created.layout_element[name] = qobject
        layouts_created.provenance[
            name] = record.file_location

    def _process_children(self, parent_qobject, record, layouts_created):
        """
        Adds each of the children cited by the InputTextRecord provided to
        the given parent QObject.
        :param parent_qobject:
        :param record:
        :param layouts_created:
        :return:
        """
        for child_name in record.child_names:
            # Using '<>' as a child name is a special case that means
            # addStretch() - on a QBoxLayout parent.
            if child_name == '<>':
                self._do_add_stretch_special_case(parent_qobject, record)
                continue
            # Now the general case.
            self._add_child_to_parent(child_name, parent_qobject, record,
                                      layouts_created.layout_element)

    def _add_child_to_parent(self, child_name, parent_qobject,
                             record, child_lookup_table):
        # Adds the the QLayout or QWidget object given as the child object, to
        # the given parent QLayout or QWidget. Introspects the child and parent
        # objects to decide how this should be done.
        ChildAdder.add_child_to_parent(child_name, parent_qobject,
                                           child_lookup_table, record)

    def _do_add_stretch_special_case(self, parent_qobject, record):
        """
        A special case of adding a child to a parent. Specifically, calling
        addStretch() on a QBoxLayout.
        :param parent_qobject: The parent QObject to add the stretch to.
        :param record: The InputTextRecord providing context.
        :return: Nothing.
        :raises: LayoutError.
        """
        if not isinstance(parent_qobject, QBoxLayout):
            msg = '\n'.join([
                'You cannot add a stretch to a parent that is not a',
                'QHBoxLayout, or a QVBoxLayout'])
            raise LayoutError(msg, record.file_location)
        parent_qobject.addStretch()
