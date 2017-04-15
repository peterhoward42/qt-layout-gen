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
        layouts_created = LayoutsCreated() # Will be populated, then returned.
        line_number = 0
        lines = MultilineString.get_as_left_shifted_lines(one_big_string)
        for line in lines:
            line_number += 1
            cls._process_line_wrapper(
                    line, finder, layouts_created, line_number, provenance)
        cls._assert_layouts_created_is_not_empty(layouts_created, provenance)
        return layouts_created

    # --------------------------------------------------------
    # Private below

    @classmethod
    def _process_line_wrapper(
            cls, line, finder, layouts_created, line_number, provenance):
        """
        A thin wrapper that adds line number context to exceptions raised.
        """
        try:
            cls._process_line(line, finder, layouts_created)
        except LayoutError as e:
            raise LayoutError("""
                    %s\n(Line number: %d, from %s)
                """,  (str(e), line_number, provenance))

    @classmethod
    def _process_line(cls, line, finder, layouts_created):
        parent_and_child, nothing_left = \
            cls._isolate_parent_and_child_part_of_line_only(line)
        if nothing_left:
            return

        # Amount of indentation gives us depth in parent-child hierarchy.
        # Incrementing starting at 1 for top level objects.
        depth = 1 + string_utils.measure_indent(parent_and_child) / 2
        cls._assert_have_not_skipped_a_level(depth, line, layouts_created)
        name, type_string = cls._parse_name_and_type(parent_and_child, line)
        new_qobject = QObjectMaker(finder).make(name, type_string)

        if depth > 1: # A child that must be added to a parent.
            parent_level = depth -1
            parent_object, parent_path = \
                layouts_created.most_recently_added_at_level(parent_level)
            ChildAdder.add(new_qobject, name, parent_object)
            layouts_created.register_child(new_qobject, parent_path, name)
        else: # A top-level object.
            layouts_created.register_top_level_object(new_qobject, name)

        cls._process_parenthesised_text(line, new_qobject)

    @classmethod
    def _assert_layouts_created_is_not_empty(cls, layouts_created, provenance):
        if layouts_created.is_empty():
            raise LayoutError("""
                This input provided (%s) contains nothing, or
                nothing except whitespace and comments.
                """, provenance)

    @classmethod
    def _isolate_parent_and_child_part_of_line_only(cls, line):
        # Consider this line: '    fred  QLabel(some text) # A comment'

        # Removes comments and any parenthesised segments to isolate what should
        # be two words - the name and the type word. Whilst preserving the
        # leading-space indentation.
        cls._assert_no_tabs_present(line)
        line = regex_helpers.remove_comment(line)
        line = regex_helpers.remove_parenthesis(line)
        nothing_left = len(line.strip()) == 0
        return line, nothing_left

    @classmethod
    def _parse_name_and_type(cls, working_line, full_line):
        words = (working_line.strip()).split()
        if len(words) != 2:
            raise LayoutError("""
                Cannot split this line: <%s>,
                into exactly two words,
                (after comments and parenthesis have been removed.)
            """, (full_line))
        return words

    @classmethod
    def _process_parenthesised_text(cls, line, object_to_add_text_to):
        text = regex_helpers.capture_parenthesis(line)
        if text is None:
            return
        try:
            object_to_add_text_to.setText(text)
        except Exception as e:
            raise LayoutError("""
                The attempt to call setText() with your parenthesised text
                from this line: <%s> failed.
                The underlying error reported was:
                <%s>.
                """, (line, str(e)))
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
    def _assert_have_not_skipped_a_level(cls, level, line, layouts_created):
        # Only allowed to descend levels in single steps.
        if level <= layouts_created.current_level() + 1:
            return
        raise LayoutError("""
            This line is indented too much: <%s>.
            It cannot be indented relative to the line
            above it by more than 2 spaces.
        """, (line))
