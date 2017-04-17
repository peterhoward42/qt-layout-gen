from qtlayoutbuilder.lib.line_parser import LineParser
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString


class ReFormatter(object):
    """
    This class is able to automatically re-format input text for the builder,
    such that the type-words form a neat aligned column.
    """

    # Minimum width of the gutter between names and type words.
    _MIN_GUTTER = 6

    @classmethod
    def format(cls, one_big_string):
        lines = MultilineString.get_as_left_shifted_lines(one_big_string)
        parsed_lines = [LineParser.parse_line(line) for line in lines]

        # First pass is done only to measure the longest (indent + name)
        # section present.
        widest = -1
        for parsed_line in parsed_lines:
            is_a_comment, indent, name, type_string, parenthesised = parsed_line
            if is_a_comment:
                continue
            extent = indent + len(name)
            if extent > widest:
                widest = extent

        # Second pass reconstitutes the output with the padding necessary
        # to create alignment.
        formatted_lines = []
        for parsed_line, line in zip(parsed_lines, lines):
            is_a_comment, indent, name, type_string, parenthesised = parsed_line
            if is_a_comment:
                formatted_lines.append(line)
                continue
            padding_required = widest + cls._MIN_GUTTER - (indent + len(name))
            output_line = ''
            output_line += ' ' * indent
            output_line += name
            output_line += ' ' * padding_required
            output_line += type_string
            if parenthesised:
                output_line += '(%s)' % parenthesised
            formatted_lines.append(output_line)
        return '\n'.join(formatted_lines)



