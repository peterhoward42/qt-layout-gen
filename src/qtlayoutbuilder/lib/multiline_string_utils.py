from qtlayoutbuilder.lib import string_utils
from qtlayoutbuilder.lib.string_utils import get_leading_spaces


class MultilineString(object):
    """
    Tools to work with multi-line, triple-quoted strings; mainly to 
    make writing unit tests easier.
    """

    @classmethod
    def shift_left(cls, input_string):
        """
        Returns a modified version of the multiline input string, that has [N]
        space characters removed from the left hand side of every
        constituent line, where [N] is the longest amount of leading whitespace
        that ALL the lines have in common.

        It assumes that any leading or trailing lines that are empty or contain
        only whitespace can be discarded. Which makes it easier to write 
        triple quoted input strings where the body starts on the line below 
        the opening triple quote and ends on the line before the closing 
        triple quote.
        """
        topped_and_tailed = MultilineString.remove_empty_first_and_last_lines(
            input_string)
        lines = topped_and_tailed.split('\n')
        shortest = 999
        shortest_string = ''
        for line in lines:
            string, length = get_leading_spaces(line)
            if length < shortest:
                shortest = length
                shortest_string = string
        new_lines = [line.replace(shortest_string, '', 1) for line in lines]
        result = '\n'.join(new_lines)
        return result

    @classmethod
    def get_as_left_shifted_lines(cls, multiline_string):
        """
        Similar to the shift_left() function above, but returns the result,
        as an array of the lines thus formed.
        """
        shifted = cls.shift_left(multiline_string)
        return shifted.split('\n')

    @classmethod
    def remove_empty_first_and_last_lines(cls, input_string):
        """
        Returns a modified variant of the input string, in which leading 
        and  trailing lines that are whitespace only, are femoved.
        """
        lines = input_string.split('\n')

        # Counter intuitive to do anything if there is not at least one newline
        # present in the input.
        if len(lines) <= 2:
            return input_string

        while ((len(lines) > 0) and (len(lines[0].strip()) == 0)):
            del lines[0]
        while ((len(lines) > 0) and (len(lines[-1].strip()) == 0)):
            del lines[-1]
        return '\n'.join(lines)

    @classmethod
    def normalise(cls, input_string):
        """
        Returns a cleaned up and modified variant of the input string, which
        makes tests for equality more tolerant. It first uses
        remove_empty_first_and_last_lines() (see above), and then removes all
        leading and trailing whitespace for the remaining lines.
        """
        topped_and_tailed = cls.remove_empty_first_and_last_lines(input_string)
        lines = topped_and_tailed.split('\n')
        lines = [line.strip() for line in lines]
        return '\n'.join(lines)
