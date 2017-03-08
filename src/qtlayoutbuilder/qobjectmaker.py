"""
This module provides functions that work out what type of QObject is being
asked for in an InputTextRecord, and attempts to instantiate one and return it.
"""

def _create_parent_qobj(input_text_record):
    """
    Tries to work out what type of QObject is being
    asked for in an InputTextRecord, and attempts to instantiate one and return it.
    :param input_text_record: The InputTextRecord that specifies what type of parent object
    should be made.
    :return: (QObject, BuildError) # Only one of them will be non-None
    """

    # Is keyword being used to specify the type?

    # Is the syntax being used that means - go off and find a QObject that is already
    # instantiated?

    # Does the type field look like a QSomething?

    # Otherwise we have an error condition

    return None, None