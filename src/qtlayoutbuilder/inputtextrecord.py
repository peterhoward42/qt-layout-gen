"""
This module is responsible for defining the InputTextRecord class.
"""

import re

from layouterror import LayoutError
import keywords


class InputTextRecord(object):
    """
    This class is able to parse a string like this: 'HBOX:my_box child_a child_b'
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
        if child_name in self.child_names:
            raise LayoutError(
                'Cannot specify two children of the same name.',
                self.file_location)
        self.child_names.append(child_name)

    def _populate_from_lhs_word(self, lhs_word):
        """
        Interprets the syntax variant used (HBOX, QLayout, Find...),
        extracts the colon separated parameters, and loads these into
        the relevant fields of the object.
        :param lhs_word: The LHS word to parse.
        :return: None
        :raises: LayoutError
        """
        # First get the segments of the LHS isolated. (Which also makes sure
        # the indexing operations below are safe.)
        segments = self._get_segments_of_lhs_word(lhs_word, self.file_location)
        type_field = segments[0]  # E.g. HBOX or QLabel or Find

        if keywords.is_a_keyword(type_field):
            self.make_or_find = self.INSTANTIATE
            self.class_required = keywords.class_required_for(type_field)
            self.parent_name = segments[1]
            return

        if (segments[0] == 'Find') and (len(segments) == 3):
            self.make_or_find = self.FIND
            self.class_required = segments[1]
            self.parent_name = segments[2]
            return

        if segments[0].startswith('Q'):
            self.make_or_find = self.INSTANTIATE
            self.class_required = segments[0]
            self.parent_name = segments[1]
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
