from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib import regex_helpers, string_utils
from qtlayoutbuilder.lib.builderassertions import BuilderAssertions


class LineParser(object):

    @classmethod
    def parse_line(cls, line):
        """
        Parses one line of input and returns information about what is
        found and the composition of the line. The first two items indicate if
        the line is a comment or is a blank line.
        When so, the others are undefined. If it is not a comment or blank,
        the remaining returned items partition out: the length of the leading
        indentation string, the name string, the type string, and the contents
        of any parenthesised content after the type word.
        :param line: The line to parse.
        :return: (is_a_comment, is_blank, indent, name, type, parenthesised)
        """
        cls._assert_no_tabs_present(line)
        if line.strip().startswith('#'):
            return True, False, None, None, None, None
        if len(line.strip()) == 0:
            return False, True, None, None, None, None
        original_line = line
        parenthesised = regex_helpers.capture_parenthesis(original_line)
        working_line = regex_helpers.remove_parenthesis(original_line)
        indent = cls._measure_and_validate_indent(working_line)
        name, type_string = cls._parse_name_and_type(working_line)
        return False, False, indent, name, type_string, parenthesised

    # --------------------------------------------------------
    # Private below

    @classmethod
    def _measure_and_validate_indent(cls, working_line):
        indent = string_utils.measure_indent(working_line)
        BuilderAssertions.assert_multiple_of_two(indent)
        return indent

    @classmethod
    def _parse_name_and_type(cls, working_line):
        words = (working_line.strip()).split()
        if len(words) != 2:
            raise LayoutError("""
                Cannot split this line, into exactly two words,
                (after comments and parenthesis have been removed.)
            """, ())
        return words

    @classmethod
    def _assert_no_tabs_present(cls, line):
        if '\t' in line:
            raise LayoutError("""
                This line contains a tab - which is not allowed.
            """, ())
