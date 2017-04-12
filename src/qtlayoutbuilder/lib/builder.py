from qtlayoutbuilder.api import LayoutsCreated, LayoutError
from qtlayoutbuilder.lib import regex_helpers
from qtlayoutbuilder.lib.childadder import ChildAdder
from qtlayoutbuilder.lib.qobjectmaker import QObjectMaker
from qtlayoutbuilder.lib.widgetandlayoutfinder import WidgetAndLayoutFinder

class Builder(object):


    @classmethod
    def build(self, lines, provenance):

        # Helpers.
        finder = WidgetAndLayoutFinder()  # (Expensive construction)

        # State used for interpretation.
        line_number = 0
        current_indent = 0  # Number of leading spaces.
        current_parent_at_level = {} # Keyed on indent.

        layouts_created = LayoutsCreated()

        try:
            for original_line in lines:
                line_number += 1

                # Prepare and analyse the line.
                self._assert_no_tabs_present(original_line)
                line = regex_helpers.with_hash_style_comment_removed(original_line)
                if self._nothing_left(line):
                    continue

                parenthesised, remainder = \
                    regex_helpers.isolate_parenthesised_bit(line)
                indent = self._measure_indent(remainder)
                name, type_word = self._isolate_two_words(remainder)

                # Create the parent child relationship for this line.
                parent_indent = indent - 2
                parent_object = current_parent_at_level[parent_indent]
                child_object = QObjectMaker(finder).make(name)
                ChildAdder.add(child_object, parent_object)

                # Register the new object in the LayoutsCreated object we will
                # return.
                layouts_created.register_object(child_object,
                        self._generate_name_path_string())

                # Do the interpretation state housekeeping.
                self._update_most_recent_update_at_level_info(indent,
                        child_object, current_parent_at_level)

                return layouts_created

        except LayoutError as e:
            raise LayoutError(self._augment_with_context(str(e), line_number,
                    provenance))

    # --------------------------------------------------------
    # Private below


    @classmethod
    def _measure_indent(cls, line):
        indent = len(line) - len(line.lstrip())
        cls._assert_multiple_of_two(indent, line)
        return indent

    @classmethod
    def _isolate_two_words(cls, line):
        line = line.strip()
        words = line.split()
        if len(words) == 2:
            return words
        msg = '\n'.join((
            'Cannot isolate two words from this line: <%s>,',
            'after removing comments and parenthesised parts if present.',
        )) % (line)
        raise LayoutError(msg)

    @classmethod
    def _nothing_left(cls, line):
        line = line.strip()
        return len(line) == 0

    @classmethod
    def _augment_with_context(cls, msg, line_number, provenance):
        return msg + '\n(Line number %d of %s)' % (line_number, provenance)

    #-------------------------------------------------------------------------
    # Assertions

    @classmethod
    def _assert_multiple_of_two(self, indent, line):
        if indent % 2 == 0:
            return
        msg = '\n'.join((
                'Indentation spaces must be a multiple of 2.',
                'This line: <%s> is indented by %d spaces.',
        )) % (line, indent)
        raise LayoutError(msg)

    @classmethod
    def _assert_no_tabs_present(self, line):
        if '\t' not in line:
            return
        msg = '\n'.join((
            'This line: <%s> contains a tab character -',
            'which is not allowed.',
        )) % (line)
        raise LayoutError(msg)
