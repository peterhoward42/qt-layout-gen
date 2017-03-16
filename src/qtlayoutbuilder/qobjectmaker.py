"""
This module is responsible for instantiating (or finding) QObjects, like
QHBoxLayout, or QLabel - taking its instructions from an InputTextRecord.
"""

from exceptions import NotImplementedError

from PySide.QtGui import *  # for the benefit of _make_qtype():

import keywords
from layouterror import LayoutError
from inputsplitter import InputTextRecord


def make_from_record(record):
    """
    Entry point for the QObject-making operation. It returns the QObject and
    parent name that has been extracted from the record. E.g. a QHBoxLayout
    object, and 'my_page'.
    :param record: The InputTextRecord to make the QObject parent for.
    :return: (QObject, name)
    :raises LayoutError
    """

    if record.instantiate_or_find_existing == InputTextRecord.INSTANTIATE:
        q_object = _instantiate_q_object(record)
        return q_object, record.parent_name
    elif record.make_or_find == InputTextRecord.FIND:
        q_object = _find_q_object(record)
        return q_object, record.parent_name
    else:
        raise NotImplementedError('should never be reached.')


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


def _find_q_object(record):
    # isolate class and name to look for
    # ask introspection utility how many references there are to an object
    # of the given type and with the given name
    # if one use that object
    # if zero complain about not found
    # if > 1 complain about ambiguity
    pass