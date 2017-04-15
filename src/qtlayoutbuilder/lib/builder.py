from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib import regex_helpers
from qtlayoutbuilder.lib import string_utils
from qtlayoutbuilder.lib.childadder import ChildAdder
from qtlayoutbuilder.lib.layoutscreated import LayoutsCreated
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString
from qtlayoutbuilder.lib.qobjectmaker import QObjectMaker
from qtlayoutbuilder.lib.widgetandlayoutfinder import WidgetAndLayoutFinder

class Builder(object):

    @classmethod
    def build(cls, one_big_string, provenance):

        finder = WidgetAndLayoutFinder() # A helper.
        layouts_created = LayoutsCreated()
        line_number = 0
        lines = MultilineString.get_as_left_shifted_lines(one_big_string)
        for line in lines:
            line_number += 1
            # Catch all LayoutExceptions, so that we can add the line
            # number and provenance to them before re-emitting them.
            try:
                cls._process_line(line, finder, layouts_created)
            except LayoutError as e:
                raise LayoutError("""
                    %s\n(Line number: %d, from %s)
                """,  (str(e), line_number, provenance))
        if layouts_created.is_empty():
            raise LayoutError("""
                This input provided (%s) contains nothing, or
                nothing except whitespace and comments.
                """, provenance)
        return layouts_created

    # --------------------------------------------------------
    # Private below

    @classmethod
    def _process_line(cls, line, finder, layouts_created):

        cls._assert_no_tabs_present(line)
        working_line = regex_helpers.remove_comment(line)
        if cls._nothing_significant_remains(working_line):
            return
        working_line = regex_helpers.remove_parenthesis(working_line)
        # No indent is top level (level 1). First level of indent is level 2.
        level = 1 + string_utils.measure_indent(working_line) / 2
        cls._assert_have_not_skipped_a_level(level, line, layouts_created)
        words = string_utils.as_list_of_words(working_line)
        cls._assert_is_two_words(words, line)
        name, type_string = words
        created = QObjectMaker(finder).make(name, type_string)
        if level > 1: # A child that must be added to a parent.
            parent_level = level -1
            parent_object, parent_path = \
                layouts_created.most_recently_added_at_level(parent_level)
            ChildAdder.add(created, name, parent_object)
            layouts_created.register_child(created, parent_path, name)
        else: # A top-level object.
            layouts_created.register_top_level_object(created, name)

    @classmethod
    def _nothing_significant_remains(cls, line):
        return len(line.strip()) == 0

    #-------------------------------------------------------------------------
    # Assertions

    @classmethod
    def _assert_multiple_of_two(self, indent, line):
        if indent % 2 == 0:
            return
        raise LayoutError("""
            Indentation spaces must be a multiple of 2.
            This line: <%s> is indented by %d spaces.
            """, (line, indent))

    @classmethod
    def _assert_no_tabs_present(self, line):
        if '\t' not in line:
            return
        raise LayoutError("""
            This line: <%s> contains a tab character -
            which is not allowed.
            """, (line))

    @classmethod
    def _assert_is_two_words(cls, words, line):
        if len(words) == 2:
            return
        raise LayoutError("""
            Cannot split this line: <%s>,
            into exactly two words,
            (after comments and parenthesis have been removed.)
        """, (line))


    @classmethod
    def _assert_have_not_skipped_a_level(cls, level, line, layouts_created):
        # Only allowed to descend levels in single steps.
        if level <= layouts_created.current_level() + 1:
            return
        raise LayoutError("""
            This line is indented too much: <%s>.
            It cannot be indented relative to the line
            above it by more than 2 spaces.
        """, (line))
