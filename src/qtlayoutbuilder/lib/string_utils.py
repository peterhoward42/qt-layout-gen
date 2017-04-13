class MultilineString(object):
    """
    Tools to work with multi-line, triple-quoted strings; mainly to make writing
    unit tests easier.
    """

    @classmethod
    def shift_left(cls, input_string):
        """
        Returns a modified version of the multiline input string, that has [N]
        space characters removed from the left hand side of every
        constituent line, where [N] is the longest amount of leading whitespace
        that ALL the lines have in common.

        It assumes that if the first and last lines are solely whitespace
        they can be discarded  - which makes it easier to write triple quoted
        input strings where the body starts on the line below the opening triple
        quote and ends on the line before the closing triple quote.
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
    def remove_empty_first_and_last_lines(cls, input_string):
        """
        Returns a modified variant of the input string, in which the first
        and last lines are removed if they contain only whitespace. Let's you
        write triple quoted strings with the main body on separate lines from
        the opening and closing quotes and then have the first and last partial
        lines thus created ignored.
        """
        lines = input_string.split('\n')

        first_line = lines[0]
        stripped = first_line.strip()
        if len(stripped) == 0:
            lines = lines[1:]

        last_line = lines[len(lines) - 1]
        stripped = last_line.strip()
        if len(stripped) == 0:
            lines = lines[:-1]
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

#----------------------------------------------------------------------------
# Ordinary string functions.

def get_leading_spaces(input_string):
    """
    Returns the leading spaces from a string and the length of that string.
    (string, length).
    """
    justified = input_string.lstrip()
    length = len(input_string) - len(justified)
    string = ' ' * length
    return string, length
