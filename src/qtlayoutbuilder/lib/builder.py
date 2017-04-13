from qtlayoutbuilder.api import LayoutsCreated, LayoutError
from qtlayoutbuilder.lib import regex_helpers
from qtlayoutbuilder.lib.childadder import ChildAdder
from qtlayoutbuilder.lib.error_utils import raise_layout_error
from qtlayoutbuilder.lib.qobjectmaker import QObjectMaker
from qtlayoutbuilder.lib.string_utils import MultilineString
from qtlayoutbuilder.lib.widgetandlayoutfinder import WidgetAndLayoutFinder

class Builder(object):


    @classmethod
    def build(self, one_big_string, provenance):

        # Helpers.
        finder = WidgetAndLayoutFinder()  # (Expensive construction)

        # While our algorithm is stateful, we use a stateless class and solely
        # class methods, so that the functions in the call stack get everything
        # they need from injected parameters. Because this makes them easier
        # to test independently, and makes the management of state less
        # fragile.

        # The state is held in these local variables, and are passed down
        # the call chain as necessary.
        line_number = 0
        current_indent = 0  # Number of leading spaces.
        current_parent_at_level = {} # Keyed on indent.

        # This is the object we will build and eventually, return.
        layouts_created = LayoutsCreated()

        # Split input into an array of lines.
        lines = MultilineString.get_as_left_shifted_lines(one_big_string)

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

                # Create the child object.
                child_object = QObjectMaker(finder).make(name)

                # Unless this is a top level object, add it to its parent.
                if indent >= 2:
                    parent_indent = indent - 2
                    parent_object = current_parent_at_level[parent_indent]
                    ChildAdder.add(child_object, parent_object)

                # Register the new object in the LayoutsCreated object we will
                # return.
                layouts_created.register_object(child_object,
                        self._generate_name_path_string())

                # Do the interpretation state housekeeping.
                self._update_interpretation_state()

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
        raise_layout_error("""
            Cannot isolate two words from this line: <%s>,
            (after removal of comments and parenthesis).
        """, (line))

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
        raise_layout_error("""
            Indentation spaces must be a multiple of 2.
            This line: <%s> is indented by %d spaces.
            """, (line, indent))

    @classmethod
    def _assert_no_tabs_present(self, line):
        if '\t' not in line:
            return
        raise_layout_error("""
            This line: <%s> contains a tab character -
            which is not allowed.
            """, (line))
