from unittest import TestCase

from builderror import BuildError

class TestBuildError(TestCase):

    def test_that_multiple_pushed_messages_are_formatted_properly_when_asked_for(self):
        err = BuildError()
        err.push_message('message about error details')
        err.push_message('message about error context')
        formatted_message = err.format_as_single_string()
        self.assertEquals(formatted_message, 'message about error context\nmessage about error details')

