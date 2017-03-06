"""
This module is responsible for knowing what keywords (like VBOX) the
layout builder recognizes.
"""

import re

KEYWORD_ALTERNATIVES_REGEX = re.compile(r'HBOX|VBOX|STACK|SPLIT|TAB')