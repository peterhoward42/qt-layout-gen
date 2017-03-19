
class LayoutError(Exception):
    """
    The one and only Exception type thrown from this package. The default
    string representation is a comprehensive user-facing message, which
    includes the input file name and line number that caused the problem.
    """

    def __init__(self, message, file_location):
        """
        Code that raises this exception should pass in a human-friendly
        string message and a FileLocation object to carry information about
        which bit of the input text caused the error.
        :param message: The message.
        :param file_location:  The FileLocation object.
        """
        super(Exception, self).__init__(message)
        self._file_location = file_location

    def __str__(self):
        return self.message + ', (%s)' % self._file_location
