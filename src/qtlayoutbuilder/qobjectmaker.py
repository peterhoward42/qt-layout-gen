"""
This module is responsible for instantiating (or finding previously
instantiated) QObjects, like QHBoxLayout, or QLabel - taking its mandate from
an InputTextRecord.
"""

from exceptions import NotImplementedError

from PySide.QtGui import *  # for the benefit of _make_qtype():

from layouterror import LayoutError
from inputsplitter import InputTextRecord


def make_from_record(record, object_finder):
    """
    Entry point for the QObject-making operation. It returns the QObject and
    parent name that has been extracted from the record. E.g. a QHBoxLayout
    object, and 'my_page'.
    :param record: The InputTextRecord to make the QObject parent for.
    :param object_finder: You must provide an initialised ObjectFinder.
    :return: (QObject, name)
    :raises LayoutError
    """

    if record.make_or_find == InputTextRecord.INSTANTIATE:
        return _instantiate_q_object(record), record.parent_name
    elif record.make_or_find == InputTextRecord.FIND:
        return _find_q_object(record, object_finder), record.parent_name
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


def _find_q_object(record, object_finder):
    """
    Tries to find an already-instantiated object that is derived from
    QWidget or QLayout, and that has
    Raises LayoutError if the instantiation fails, or if the object thus
    created in not a QWidget or QLayout.
    :param record: The InputTextRecord defining what is required.
    :return: QObject
    """

    fart come back to here once object finder is rationalised


    found_objects = object_finder.find_objects(record.parent_name)
    if len(found_objects) == 0:
        raise LayoutError(
            '\n'.join([
                'Cannot find any objects of class: <%s>,',
                'that are referenced by a variable called: <%s>.',
                ]) %
            (record.class_required, record.parent_name), record.file_location)
    if len(found_objects) > 1:
        raise LayoutError(
            '\n'.join([
                'Ambiguity Problem: Found more than one objects of class: <%s>,',
                'that is referenced by a variable called: <%s>.',
            ]) %
            (record.class_required, record.parent_name), record.file_location)
    # When it works...
    return found_objects[0]
