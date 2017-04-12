import re


def with_hash_style_comment_removed(input_string):
    # I.e. comment defined as '#' up to end of line.
    return _COMMENT_REGEX.sub('', input_string)

def isolate_parenthesised_bit(line):
    # Returns (the-stuff-inside-brackets, remainder).
    # Where remainder is the original line from which the parenthesised
    # bit has been removed.
    found = _PARENTHESIS_REGEX.match(line)
    if not found:
        return '', line
    groups = found.groups()
    # Remainder is the bits before and after the parenthesised bit, glued
    # back together.
    remainder = groups[0] + groups[2]
    # Strip the brackets themselves off what we return as the parenthesised
    # bit.
    paren = groups[1][1:-1]
    return paren, remainder

_PARENTHESIS_REGEX = re.compile(r'([^(]*)(\(.*\))(.*)')
_COMMENT_REGEX = re.compile(r'#.*')
