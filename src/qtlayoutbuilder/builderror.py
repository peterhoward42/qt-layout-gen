""" Module defines the class BuildError. """


class BuildError(object):
    """
    A container for a stack-like sequence of error messages.
    Designed to make it convenient for an error message to be augmented
    with context information as it passes back up a call chain.
    """

    def __init__(self, initial_message):
        """
        :param initial_message: The message with which to initialise the error stack.
        """
        self._messages = [initial_message, ]

    def extended_with(self, message):
        """
        Effectively extends the error stack by prepending the incoming
        message, but does so by making and returning a new object.
        :param message: The message to add.
        :return: The new BuildError.
        """
        new_err = BuildError(message)
        new_err._messages.extend(self._messages)
        return new_err

    def format_as_single_string(self):
        """
        Provides a single string representation of the error stack.
        :return: The string representation.
        """
        return '\n'.join(self._messages)
