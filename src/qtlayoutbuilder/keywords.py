"""
This module is responsible for knowing what keywords (like VBOX) the
layout builder recognizes, and providing utility functions concerned with keywords.
"""

import re

WORDS = ['HBOX', 'VBOX', 'STACK', 'SPLIT', 'TAB']

_keyword_regex = re.compile('|'.join(WORDS))


def starts_with_keyword(some_text):
    """
    Assesses if the given string starts with a recognized keyword.
    :param some_text: The text to test.
    :return: Either the keyword that was recognized, or None
    """
    match = _keyword_regex.match(some_text)
    if match:
        return match.group()
    return None


def mark_all_keywords_found(some_text, marking_callback):
    """
    Returns a copy of the input text, in which every instance of a keyword has been
    replaced with whatever is returned by your callback. Your callback is called for
    each keyword found and will receive
    a single argument, which is the regex match object. This match object provides access
    to the keyword found in match.group(), and hence the function can use the keyword as
    part of the replacement text it mandates. I.e. by adding something it can "mark" it.
    :param some_text: The text to search for keywords in. (See regex.sub())
    :param marking_callback: Your callback.
    :return: The modified text.
    """
    return _keyword_regex.sub(marking_callback, some_text)

