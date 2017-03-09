"""
Module to define the LayoutError class.
"""


class LayoutError(Exception):
    """
    The one and only Exception thrown by this library.
    It has two design intents. Firstly that the default string representation will be suitable as a user-facing
    message. Secondly that sufficient context will be passed down to the places that raise these errors, that
    seldom will layers above in the call stack have any need to catch them to add context.
    """

    def __init__(self, message, file_location):
        """
        Pass in a string message and a FileLocation object when available. (else None)
        :param message: The message.
        :param file_location:  The FileLocation object.
        """
        super(Exception, self).__init__(message)
        self._file_location = file_location

    def __str__(self):
        if self._file_location:
            return self.message + ', (%s) % self._file_location'
        else:
            return self.message
