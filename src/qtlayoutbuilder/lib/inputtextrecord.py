"""
This module is responsible for defining the InputTextRecord class.
"""

import re

import qtlayoutbuilder.lib.keywords
from qtlayoutbuilder.api.layouterror import LayoutError


class InputTextRecord(object):
    """
    This class is able to parse a string like this: 'my_box:HBOX child_a child_b'
    and build a structured model from it that isolates the field and captures
    the intent.
    It also holds a FileLocation - which remembers the source filename and
    line number to help with error handling later on.
    """

    # Should the QObject for the LHS be created, or an existing one found?
    INSTANTIATE = 'instantiate'
    FIND = 'find'

    def __init__(self, file_location):
        self.file_location = file_location  # a FileLocation
        self.make_or_find = None  # INSTANTIATE | FIND
        self.class_required = None  # A string. E.g. 'QString', 'MyCustomClass'
        self.parent_name = None
        self.child_names = []

    @classmethod
    def make_from_lhs_word(cls, lhs_word, file_location):
        """
        This factory function helps you create an InputTextRecord, when
        all you have is the LHS word. E.g. 'HBOX:my_box'.
        You can call add_child_word() repeatedly to augment it afterwards.
        It raises a LayoutError if the given LHS word is (lexically)
        malformed.
        :param lhs_word: The word to use to initialise the LHS.
        :file_location: A FileLocation
        :return: The newly constructed InputTextRecord.
        :raises: LayoutError
        """
        trimmed_lhs = lhs_word.strip()
        record = InputTextRecord(file_location)
        record._populate_from_lhs_word(trimmed_lhs)
        return record

    @classmethod
    def make_from_all_words(cls, all_words, file_location):
        """
        This factory function helps you create an InputTextRecord, when
        you have all the constituent words. E.g. ('HBOX:my_box', 'child_a', 'child_b').
        It raises a LayoutError if the given LHS word is (lexically)
        malformed.
        :param: all_words: The words to use to initialise the LHS.
        :file_location: A FileLocation
        :return: The newly constructed InputTextRecord.
        :raises: LayoutError
        """
        if len(all_words) == 0:
            raise LayoutError('Cannot deal with empty list of words', file_location)
        lhs_word = all_words[0]
        # Delegate to the sister factory function - which will do
        # the necessary error handling.
        record = cls.make_from_lhs_word(lhs_word, file_location)
        if len(all_words) > 1:
            for child_name in all_words[1:]:
                record.add_child_name(child_name)
        return record

    def add_child_name(self, child_name):
        """
        Adds the given child name to the list of children being held.
        :param child_name: The child name to add.
        :return: None
        :raises: LayoutError
        """
        # In general disallow the presence of two child names that same,
        # but make exception for the special case of '<>'.
        if child_name in self.child_names:
            if child_name != '<>':
                raise LayoutError(
                    'Cannot specify two children of the same name.',
                    self.file_location)
        self.child_names.append(child_name)

    @classmethod
    def mock_record(cls):
        words = ['QLabel:my_label', 'a', 'b']
        record = InputTextRecord.make_from_all_words(
            words, cls.mock_file_location())
        return record

    @classmethod
    def mock_file_location(cls):
        return 'no-such-file'

    #-------------------------------------------------------------------------
    # Private below.

    def _populate_from_lhs_word(self, lhs_word):
        """
        Interprets the syntax variant used (HBOX, QLayout, Find...),
        extracts the colon separated parameters, and loads these into
        the relevant fields of the object.
        :param lhs_word: The LHS word to parse.
        :return: None
        :raises: LayoutError
        """

        # my_label:QLabel
        # my_label:VBOX
        # my_thing:Find:MyClass

        segments = self._get_segments_of_lhs_word(lhs_word, self.file_location)
        type_field = segments[1]  # QLabel | VBOX | Find
        self.parent_name = segments[0]

        if qtlayoutbuilder.lib.keywords.is_a_keyword(type_field):
            self.make_or_find = self.INSTANTIATE
            self.class_required = qtlayoutbuilder.lib.keywords.class_required_for(type_field)
            return

        if (type_field == 'Find') and (len(segments) == 3):
            self.make_or_find = self.FIND
            self.class_required = segments[2]
            return

        if type_field.startswith('Q'):
            self.make_or_find = self.INSTANTIATE
            self.class_required = type_field
            return

        raise LayoutError(
            'Cannot detect any of the allowed forms in this left hand side: <%s>' % lhs_word,
            self.file_location)

    _WHITESPACE_REGEX = re.compile('\s')

    @classmethod
    def _get_segments_of_lhs_word(cls, lhs_word, file_location):
        """
        Splits the given LHS word (like HBOX:my_box) into its constituent
        segments and returns them as a sequence.
        :return: The sequence of segments.
        :raises: LayoutError
        """
        if cls._WHITESPACE_REGEX.search(lhs_word):
            raise LayoutError(
                'Left hand side word: <%s>, must not contain whitespace' % lhs_word,
                file_location)
        segments = lhs_word.split(':')
        # Produced any empty segments?
        if len([seg for seg in segments if len(seg) == 0]) != 0:
            raise LayoutError(
                ('One of the segments produced by splitting this word: <%s> using colons ' + \
                 'is empty') % lhs_word,
                file_location)
        if (len(segments) < 2) or (len(segments) > 3):
            raise LayoutError(
                ('Splitting this word: <%s> using colons ' + \
                 'does not produce 2 or 3 segments as required.') % lhs_word,
                file_location)
        return segments

