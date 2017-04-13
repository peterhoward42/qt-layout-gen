class MultilineString(object):
    """
    Tools to work with multi-line, triple-quoted strings.
    """

    @classmethod
    def shift_left(cls, input_string):
        """
        Returns a modified version of the multiline input string, that has [N]
        space characters removed from the left hand side of every
        constituent line, where [N] is the longest amount of leading whitespace
        that all the lines have in common.

        It assumes that if the first line is solely whitespace it can be
        discarded so that you can write input strings that start their body
        on the line after the first triple quote.
        """
        lines = MultilineString.remove_empty_first_line(input_string)
        lines = input_string.split('\n')
        shortest = 999
        shortest_string = ''
        for line in lines:
            string, length = get_leading_spaces(line)
            if length < shortest:
                shortest = length
                shortest_string = string
        new_lines = [line.replace(shortest_string, '', 1) for line in lines]
        return '\n'.join(new_lines)

    @classmethod
    def remove_empty_first_line(cls, input_string):
        """
        Returns a modified variant of the input string, in which the first
        line is removed if it contains only whitespace.
        """
        lines = input_string.split('\n')
        first_line = lines[0]
        stripped = first_line.strip()
        if len(stripped) == 0:
            return input_string[1:]
        else:
            return input_string[0:] # We promised to not mutate the input.

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
