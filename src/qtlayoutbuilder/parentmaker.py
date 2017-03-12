"""
This module is responsible for making (or finding) the QObject that
an InputTextRecord is asking for. (Like a QHBoxLayout).
"""

from exceptions import NotImplementedError

from PySide.QtGui import * # for the benefit of _make_qtype():

import keywords
from layouterror import LayoutError
from inputsplitter import InputTextRecord

def make(record):
    """
    Entry point for the QObject-making operation. It returns the
    QObject and parent name that has been extracted from the record.
    E.g. a QHBoxLayout object, and 'my_page' for the case above.
    :param record: The InputTextRecord to make the QObject parent for.
    :return: (QObject, name)
    :raises LayoutError
    """

    if record.make_or_find == InputTextRecord.INSTANTIATE:
        q_object = _instantiate_q_object(record)
        return (q_object, record.parent_name)
    elif record.make_or_find == InputTextRecord.FIND:
        q_object = _find_q_object(record)
        return (q_object, record.parent_name)
    else:
        raise NotImplementedError('should never be reached.')


def _instantiate_q_object(record):
    # Attempt to instantiate an object of the specified type.
    # Object if the instantiation fails
    # Object if the type produced is not instance of QLayout or QWidget
    # Return object and name

    # Does python recognize this name at runtime?
    try:
        class_name = record.class_required
        constructor = globals()[class_name]
    except KeyError as e:
        raise LayoutError(
            "Python can't make any sense of this word. (it doesn't exist in the global namespace) <%s>" % class_name,
            record.file_location)

    # Have a go at constructing it, and then make sure it is a class derived from QLayout or QWidget.
    try:
        instance = constructor()
    except Exception as e:
        raise LayoutError(('Cannot instantiate one of these: <%s>\n' +
            'It is supposed to be a QtGui class name like QString or QLabel that can be used as a constructor.\n' + \
            'When the code tried to instantiate one...\n' + \
            'the underlying error message was: <%s>') % (class_name, str(e)), record.file_location)
    # Make sure it is a QWidget or QLayout
    if (isinstance(instance, QWidget) is False) and (isinstance(instance, QLayout) is False):
        raise LayoutError(('This class name: <%s> instantiates successfully, but is neither ' + \
            'a QLayout nor a QWidget') % class_name, record.file_location)


def _find_q_object(record):
    return 42

