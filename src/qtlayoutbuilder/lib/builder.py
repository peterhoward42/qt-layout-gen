from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib import regex_helpers
from qtlayoutbuilder.lib import string_utils
from qtlayoutbuilder.lib.builderassertions import BuilderAssertions
from qtlayoutbuilder.lib.childadder import ChildAdder
from qtlayoutbuilder.lib.layoutscreated import LayoutsCreated
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString
from qtlayoutbuilder.lib.original_file_rewriter import OriginalFileReWriter
from qtlayoutbuilder.lib.qobjectmaker import QObjectMaker
from qtlayoutbuilder.lib.widgetandlayoutfinder import WidgetAndLayoutFinder

class Builder(object):

    @classmethod
    def build(cls, one_big_string, provenance, tidy_and_overwrite):
        finder = WidgetAndLayoutFinder() # A helper.
        layouts_created = LayoutsCreated() # Will be populated, then returned.
        overwriter = OriginalFileReWriter(provenance)
        line_number = 0
        lines = MultilineString.get_as_left_shifted_lines(one_big_string)
        for line in lines:
            line_number += 1
            cls._process_line_wrapper(line, finder, layouts_created,
                    line_number, provenance, overwriter)
        BuilderAssertions.assert_layouts_created_is_not_empty(
                layouts_created, provenance)
        if tidy_and_overwrite:
            overwriter.overwrite_original_file()
        return layouts_created

    # --------------------------------------------------------
    # Private below

    @classmethod
    def _process_line_wrapper(cls, line, finder, layouts_created,
            line_number, provenance, overwriter):
        # A thin wrapper that adds line number context to exceptions raised.
        try:
            cls._process_line(line, finder, layouts_created, overwriter)
        except LayoutError as e:
            raise LayoutError("""
                    %s
                    (This line: <%s>)
                    (Line number: %d, from %s)
                """,  (str(e), line, line_number, provenance))

    @classmethod
    def _process_line(cls, line, finder, layouts_created, overwriter):
        overwriter.register_line(line)
        parent_and_child, nothing_left = \
            cls._isolate_parent_and_child_part_of_line_only(line)
        if nothing_left:
            return

        # Amount of indentation gives us depth in parent-child hierarchy.
        # Incrementing starting at 1 for top level objects.
        indent = string_utils.measure_indent(parent_and_child)
        BuilderAssertions.assert_multiple_of_two(indent)
        depth = 1 + indent / 2
        BuilderAssertions.assert_have_not_skipped_a_level(
                depth, line, layouts_created)
        name, type_string = cls._parse_name_and_type(parent_and_child, line)
        overwriter.register_name_for_most_recently_registered_line(name)
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
    def _isolate_parent_and_child_part_of_line_only(cls, line):
        # Consider this line: '    fred  QLabel(some text) # A comment'

        # Removes comments and any parenthesised segments to isolate what should
        # be two words - the name and the type word. Whilst preserving the
        # leading-space indentation.
        BuilderAssertions.assert_no_tabs_present(line)
        line = regex_helpers.remove_comment(line)
        line = regex_helpers.remove_parenthesis(line)
        nothing_left = len(line.strip()) == 0
        return line, nothing_left

    @classmethod
    def _parse_name_and_type(cls, working_line, full_line):
        words = (working_line.strip()).split()
        if len(words) != 2:
            raise LayoutError("""
                Cannot split this line, into exactly two words,
                (after comments and parenthesis have been removed.)
            """, ())
        return words

    @classmethod
    def _process_parenthesised_text(cls, line, object_to_add_text_to):
        text = regex_helpers.capture_parenthesis(line)
        if text is None:
            return
        if hasattr(object_to_add_text_to, 'setText'):
            object_to_add_text_to.setText(text)
            return
        if hasattr(object_to_add_text_to, 'setTitle'):
            object_to_add_text_to.setTitle(text)
            return
        raise LayoutError("""
            Cannot do anything with the text you specified
            in parenthesis because the object being created
            has neither the setText(), nor the setTitle() method.
            """, ())




