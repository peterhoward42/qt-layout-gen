from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib import regex_helpers
from qtlayoutbuilder.lib import string_utils
from qtlayoutbuilder.lib.builderassertions import BuilderAssertions


class LineParser(object):

    @classmethod
    def parse_line(cls, line):
        """
        Parses one line of input and returns information about what is
        found and the composition of the line. The first item in the returned
        sequence indicates if the line is a comment, and when so, the others
        are undefined. If it is not a comment the remaining returned items
        partition out: the length of the leading indentation strings, the name
        string, the type string, and the contents of any parenthesised
        content after the type word.
        :param line: The line to parse.
        :return: (is_a_comment, indent, name, type, parenthesised)
        """
        if line.strip().startswith('#'):
            return True, None, None, None, None
        original_line = line
        parenthesised = regex_helpers.capture_parenthesis(original_line)
        working_line = regex_helpers.remove_parenthesis(original_line)
        indent = cls._measure_and_validate_indent(working_line, original_line)
        name, type_string = cls._parse_name_and_type(
                working_line, original_line)
        return False, indent, name, type_string, parenthesised

    # --------------------------------------------------------
    # Private below

    @classmethod
    def _measure_and_validate_indent(cls, working_line, original_line):
        indent = string_utils.measure_indent(working_line)
        BuilderAssertions.assert_multiple_of_two(indent)
        return indent

    @classmethod
    def _parse_name_and_type(cls, working_line, full_line):
        words = (working_line.strip()).split()
        if len(words) != 2:
            raise LayoutError("""
                Cannot split this line, into exactly two words,
                (after comments and parenthesis have been removed.)
            """, ())
        return words
