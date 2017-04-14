import re


def remove_comment(input_string):
    # I.e. comment defined as '#' up to end of line.
    return _COMMENT_REGEX.sub('', input_string)

def remove_parenthesis(line):
    return _PARENTHESIS_REGEX.sub('', line)

_PARENTHESIS_REGEX = re.compile(r'\(.*\)')
_COMMENT_REGEX = re.compile(r'#.*')
