""" Module defines the class BuildError. """


class BuildError(object):
    """ Encapsulates a multi-line, human-friendly error message.
    """

    def __init__(self):
        self._messages = []

    def push_message(self, message):
        """ Add a message string to the existing stack. """
        self._messages.insert(0, message)

    def format_as_single_string(self):
        """ Provide the messages concatenated, with a newline between each
        one."""
        return '\n'.join(self._messages)
