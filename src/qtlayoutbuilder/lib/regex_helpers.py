"""
Utility functions that do regex stuff.
"""

import re


def remove_comment(input_string):
    # I.e. comment defined as '#' up to end of line.
    return _COMMENT_REGEX.sub('', input_string)

def remove_parenthesis(line):
    return _PARENTHESIS_REGEX.sub('', line)

def capture_parenthesis(line):
    match = _PARENTHESIS_REGEX.search(line)
    if not match:
        return None
    paren = match.group(0)  # Includes the brackets.
    if len(paren) == 2:
        return None
    return paren[1:-1]


_PARENTHESIS_REGEX = re.compile(r'\(.*\)')
_COMMENT_REGEX = re.compile(r'#.*')
