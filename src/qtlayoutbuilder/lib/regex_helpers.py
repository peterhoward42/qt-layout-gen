import re


def with_hash_style_comment_removed(input_string):
    # I.e. comment defined as '#' up to end of line.
    return _COMMENT_REGEX.sub('', input_string)

def with_parenthesis_removed(line):
    return _PARENTHESIS_REGEX.sub('', line)

_PARENTHESIS_REGEX = re.compile(r'\(.*\)')
_COMMENT_REGEX = re.compile(r'#.*')
