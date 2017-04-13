"""
This module is responsible for knowing what keywords (like VBOX) the
layout builder recognizes, and providing utility functions concerned with
keywords.
"""

from PySide.QtGui import *

_CONSTRUCTORS = {
    'hbox'  : QHBoxLayout,
    'vbox'  : QVBoxLayout,
    'label' : QLabel,
    'button': QPushButton,
    'stack' : QStackedLayout,
    'tab'   : QTabWidget,
    'group' : QGroupBox,
    'widget': QWidget,
    'split' : QSplitter
}

def all_keywords():
    return _CONSTRUCTORS.keys()

def is_a_keyword(word):
    return word in _CONSTRUCTORS.keys()

def class_required_for(keyword):
    return _CONSTRUCTORS.get(keyword, None)
