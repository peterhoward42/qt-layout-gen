"""
This module is responsible for knowing what keywords (like VBOX) the
layout builder recognizes, and providing utility functions concerned with keywords.
"""

WORDS = ['HBOX', 'VBOX', 'STACK', 'SPLIT', 'TAB']

_CONSTRUCTORS = {
    'HBOX': 'QHBoxLayout',
    'VBOX': 'QVBoxLayout',
    'STACK': 'QStackedLayout',
    'SPLIT': 'QSplitter',
    'TAB': 'QTabWidget',
}


def is_a_keyword(word):
    return word in WORDS


def class_required_for(keyword):
    return _CONSTRUCTORS.get(keyword, None)
