"""
This module is responsible for knowing what keywords (like VBOX) the
layout builder recognizes, and providing utility functions concerned with keywords.
"""

import re

from PySide.QtGui import QLabel, QHBoxLayout, QVBoxLayout, QStackedLayout, QTabWidget, QSplitter

from layouterror import LayoutError


WORDS = ['HBOX', 'VBOX', 'STACK', 'SPLIT', 'TAB']

_CONSTRUCTORS = {
    'HBOX': QHBoxLayout,
    'VBOX': QVBoxLayout,
    'STACK': QStackedLayout,
    'SPLIT': QSplitter,
    'TAB': QTabWidget,
}

def is_a_keyword(word):
    return word in WORDS


