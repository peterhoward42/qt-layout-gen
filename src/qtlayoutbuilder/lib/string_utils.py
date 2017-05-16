"""
A few convenience functions for strings.
"""

def get_leading_spaces(input_string):
    """
    Returns the leading spaces from a string and the length of that string.
    (string, length).
    """
    justified = input_string.lstrip()
    length = len(input_string) - len(justified)
    string = ' ' * length
    return string, length

def measure_indent(line):
    return len(line) - len(line.lstrip())

def as_list_of_words(line):
    line = line.strip()
    return line.split()

def with_all_whitespace_removed(input_string):
    res = input_string
    res = res.replace(' ', '')
    res = res.replace('\t', '')
    res = res.replace('\n', '')
    return res

