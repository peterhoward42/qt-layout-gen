"""
This module is responsible for instantiating (or finding previously
instantiated) QObjects, like QHBoxLayout, or QLabel - taking its mandate from
an InputTextRecord.
"""

from exceptions import NotImplementedError

from PySide.QtGui import *  # for the benefit of _make_qtype():

from qtlayoutbuilder.lib.inputsplitter import InputTextRecord
from qtlayoutbuilder.api.layouterror import LayoutError


def make_from_parent_info(record, widget_and_layout_finder):
    """
    Entry point for the QObject-making operation. It returns the QObject and
    parent name that has been extracted from the record. E.g. a QHBoxLayout
    object, and 'my_page'.
    :param record: The InputTextRecord to make the QObject parent for.
    :param widget_and_layout_finder: A pre-initialised WidgetAndLayoutFinder.
    :return: (QObject, name)
    :raises LayoutError
    """

    if record.make_or_find == InputTextRecord.INSTANTIATE:
        return _instantiate_q_object(record), record.parent_name
    elif record.make_or_find == InputTextRecord.FIND:
        return _find_q_object(
            record, widget_and_layout_finder), record.parent_name
    else:
        raise NotImplementedError('should never be reached.')

#----------------------------------------------------------------------------
# Private below

def _instantiate_q_object(record):
    """
    Instantiates a QObject of the type specified in the record.
    Raises LayoutError if the instantiation fails, or if the object thus
    created in not a QWidget or QLayout.
    :param record: The InputTextRecord defining what is required.
    :return: QObject
    """

    # Does python recognize this name at runtime?
    try:
        class_name = record.class_required
        constructor = globals()[class_name]
    except KeyError as e:
        raise LayoutError(
            ' '.join([
                'Python cannot make any sense of this word. (it does not exist',
                'in the global namespace) <%s>']) %
            class_name, record.file_location)

    # Have a go at constructing it, and then make sure it is a class derived
    # from QLayout or QWidget.
    try:
        instance = constructor()
    except Exception as e:
        raise LayoutError(
            '\n'.join([
                'Cannot instantiate one of these: <%s>.',
                'It is supposed to be a QtQui class name like QString or',
                'QLabel that can be used as a constructor.',
                'When the code tried to instantiate one...',
                'the underlying error message was: <%s>']) %
            (class_name, str(e)), record.file_location)
    # Make sure it is a QWidget or QLayout
    if isinstance(instance, QWidget):
        return instance
    if isinstance(instance, QLayout):
        return instance
    raise LayoutError(
        '\n'.join([
            'This class name: <%s> instantiates successfully,',
            'but is neither a QLayout, nor a QWidget']) %
        (class_name), record.file_location)


def _find_q_object(record, widget_and_layout_finder):
    """
    Tries to find an already-instantiated QWidget or QLayout that is of
    the class specified in record.class_required, and which is referenced by a
    variable or attribute having the name specified in record.parent_name.
    :param record: The InputTextRecord providing the search mandate.
    :param widget_and_layout_finder: A pre-initialised WidgetAndLayoutFinder.
    :return: QObject
    """

    cls_name = record.class_required
    ref_name = record.parent_name

    found = widget_and_layout_finder.find(cls_name, ref_name)

    # Object to nothing found, or duplicates found.
    if len(found) == 0:
        raise LayoutError(
            '\n'.join([
                'Cannot find any objects of class: <%s>,',
                'that are referenced by a variable called: <%s>.',
                ]) %
            (cls_name, ref_name), record.file_location)
    if len(found) > 1:
        raise LayoutError(
            '\n'.join([
                'Ambiguity Problem: Found more than one objects of class: <%s>,',
                'that is referenced by a variable called: <%s>.',
            ]) %
            (cls_name, ref_name), record.file_location)

    # All is well
    return found[0]
