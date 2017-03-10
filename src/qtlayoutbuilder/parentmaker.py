"""
This module is responsible for interpreting the word from the LHS of an InputTextRecord,
like 'HBOX:my_page' and instantiating (or finding) the QObject it is calling for.
"""

import keywords
from layouterror import LayoutError

def make(record):
    """
    Entry point for the parent-making operation. It returns the
    QObject and the parent name that has been extracted from the record.
    E.g. a QHBoxLayout object, and 'my_page' for the case above.
    :param record: The InputTextRecord to make the QObject parent for.
    :return: The QObject
    :raises LayoutError
    """

    # What method should we choose to make the LHS. E.g. keyword, QType, or Find?
    # Organised thus to aid unit testing.
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
    # We can assume here (from the input splitting) that the record has a
    # left hand side, and this has at least one colon in.
    if _lhs_has_two_colons(record):
        return _find_existing_qobject
    elif _lhs_starts_with_letter_q(record):
        return _make_qtype
    elif _lhs_starts_with_keyword(record):
        return _make_keyword_type
    raise LayoutError(
            ('The left hand side: <%s> of your record does not ' + \
             'conform to any of the legal forms') % record.lhs(), record.file_location)


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


def _make_qtype(record):
    return 42


def _make_keyword_type(record):
    return 42

