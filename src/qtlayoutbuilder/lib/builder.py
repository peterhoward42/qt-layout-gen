from qtlayoutbuilder.api import LayoutsCreated, LayoutError
from qtlayoutbuilder.lib import regex_helpers
from qtlayoutbuilder.lib import string_utils
from qtlayoutbuilder.lib.childadder import ChildAdder
from qtlayoutbuilder.lib.error_utils import raise_layout_error
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString
from qtlayoutbuilder.lib.qobjectmaker import QObjectMaker
from qtlayoutbuilder.lib.widgetandlayoutfinder import WidgetAndLayoutFinder

class Builder(object):

    @classmethod
    def build(cls, one_big_string, provenance):

        finder = WidgetAndLayoutFinder() # A helper.
        layouts_created = LayoutsCreated() # Will be populated and returned.
        line_number = 0
        lines = MultilineString.get_as_left_shifted_lines(one_big_string)
        for line in lines:
            line_number += 1
            # Catch all LayoutExceptions, so that we can add the line
            # number and provenance to them before remitting them.
            try:
                cls._process_line(line, finder, layouts_created)
            except LayoutError as e:
                raise_layout_error("""
                    %s\n(Line number: %d, from %s)
                """ % (str(e), line_number, provenance))

    # --------------------------------------------------------
    # Private below

    @classmethod
    def _process_line(cls, line, finder, layouts_created):

        cls._assert_no_tabs_present(line)
        working_line = regex_helpers.with_hash_style_comment_removed(line)
        if cls._nothing_significant_remains(working_line):
            return
        working_line = regex_helpers.with_parenthesis_removed(working_line)
        level = string_utils.measure_indent(working_line) / 2
        words = string_utils.as_list_of_words(working_line)
        cls._assert_is_two_words(words, line)
        child_name, type_string = words
        child_object = QObjectMaker(finder).make(child_name)
        parent_level = level -1
        parent_object = layouts_created.most_recent_at_level(parent_level)
        ChildAdder.add(child_object, parent_object)
        layouts_created.register_object(child_object, child_name, parent_level)

    @classmethod
    def _nothing_significant_remains(cls, line):
        return len(line.strip()) == 0
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

    @classmethod
    def _assert_is_two_words(cls, words, line):
        if len(words) == 2:
            return
        raise_layout_error("""
            Cannot split this line: <%s>,
            into exactly two words,
            (after comments and parenthesis have been removed.)
        """, (line))
