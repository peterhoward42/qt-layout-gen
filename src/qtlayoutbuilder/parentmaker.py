"""
This module is responsible for interpreting the word from the LHS of an InputTextRecord,
like 'HBOX:my_page' and instantiating (or finding) the QObject it is calling for.
"""

from PySide.QtGui import * # for the benefit of _make_qtype():

import keywords
from layouterror import LayoutError

def make(record):
    """
    Entry point for the QObject-making operation. It returns the
    QObject and parent name that has been extracted from the record.
    E.g. a QHBoxLayout object, and 'my_page' for the case above.
    :param record: The InputTextRecord to make the QObject parent for.
    :return: (QObject, name)
    :raises LayoutError
    """
    # Check the record has fit for purpose LHS first. (Don't depend on
    # the earlier parsing - to avoid fragility and dependency coupling).
    _assertRecordHasWellFormedLHS(record)

    # Decide which method we should choose to make the LHS based on
    # the syntax variant used. I.e. one from: (HBOX, QLabel, Find:CustomWidget:fred)
    # We made it a function so it can be unit tested easily.
    # It returns one of the functions below, like for example '_make_qtype'.
    factory_function = _deduce_lhs_producer_function(record)
    # Use the producer to make or obtain the Qobject and the name.
    return factory_function(record)


def _deduce_lhs_producer_function(record):
    """
    Work out what mechanism the input record is asking for to produce the
    parent object. Could be in any of these styles: HBOX | QLabel | Find:Class:Name
    :param record: The record to examine.
    :return: The choice of producer function that should be used.
    """
    if _lhs_has_two_colons(record):
        return _find_existing_qobject
    elif _lhs_starts_with_letter_q(record):
        return _make_qtype
    elif _lhs_starts_with_keyword(record):
        return _make_keyword_type
    raise LayoutError(
            ('The left hand side: <%s> of your record does not ' + \
             'conform to any of the legal forms') % record.lhs(), record.file_location)

def _make_qtype(record):
    # Isolate the QType being asked for and the name.
    # Attempt to instantiate an object of that type
    # Is QtGui available to import from at this point?
    # Object if the instantiation fails
    # Object if the type produced is not instance of QLayout or QWidget
    # Return object and name

    lhs = record.lhs()
    # Fish out the alleged QObject type and the name.
    # All we can rely on, is that the lhs has a colon in it and starts with a Q.
    segments = _colon_delimited_segments(lhs)
    qword, name = [s.strip() for s in segments]
    if (len(qword) == 0) or (len(name) == 0):
        raise LayoutError(
            'When we split this left hand side at the colon: <%s>, we end up with one part that is of zero length.' %
            record.lhs(), record.file_location)
    # See if Python can resolve the name as something it knows about.
    try:
        look_up_in_python_namespace = globals()[qword]
    except KeyError as e:
        raise LayoutError(
            "Python can't make any sense of this word. (it doesn't exist in the global namespace) <%s>" % qword,
            record.file_location)
    # Have a go at constructing it, and then make sure it is a class derived from QLayout or QWidget.
    try:
        instance = look_up_in_python_namespace()
    except Exception as e:
        raise LayoutError(('Cannot instantiate one of these: <%s>\n' +
            'It is supposed to be a QtGui class name like QString or QLabel that can be used as a constructor.\n' + \
            'When the code tried to instantiate one...\n' + \
            'the underlying error message was: <%s>') % (qword, str(e)), record.file_location)
    # Make sure it is a QWidget or QLayout
    if (isinstance(instance, QWidget) is False) and (isinstance(instance, QLayout) is False):
        raise LayoutError(('This QWord: <%s> instantiates, but is neither ' + \
            'a QLayout or QWidget') % qword, record.file_location)

def _assertRecordHasWellFormedLHS(record):
    lhs = record.lhs()



def _lhs_has_two_colons(record):
    """
    Does the LHS of the record have two colons in?
    :param record:
    :return: Boolean
    """
    lhs = record.lhs()
    segments = _colon_delimited_segments(lhs)
    return len(segments) == 3


def _colon_delimited_segments(word):
    return word.split(':')


def _lhs_starts_with_letter_q(record):
    lhs = record.lhs()
    return lhs.startswith('Q')


def _lhs_starts_with_keyword(record):
    lhs = record.lhs()
    segments = _colon_delimited_segments(lhs)
    return keywords.is_a_keyword(segments[0])


def _find_existing_qobject(record):
    return 42




def _make_keyword_type(record):
    return 42

