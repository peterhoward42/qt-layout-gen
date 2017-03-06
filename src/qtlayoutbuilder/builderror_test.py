from unittest import TestCase

from builderror import BuildError


class TestBuildError(TestCase):
    def test_produces_correct_error_string_when_error_is_extended_twice(self):
        err = BuildError('message about error details')
        higher_level_err = err.extended_with('message about higher level error')
        even_higher_level_err = higher_level_err.extended_with('message about even higher level error')
        eventual_formatted_err = even_higher_level_err.format_as_single_string()
        expected = 'Error stack:\n\n1' + \
                   ': message about even higher level error\n\n' + \
                   '2: message about higher level error\n\n' + \
                   '3: message about error details\n\n'
        self.assertEquals(
            eventual_formatted_err, expected)
