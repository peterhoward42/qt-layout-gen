from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib.builderassertions import BuilderAssertions
from qtlayoutbuilder.lib.childadder import ChildAdder
from qtlayoutbuilder.lib.layoutscreated import LayoutsCreated
from qtlayoutbuilder.lib.line_parser import LineParser
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString
from qtlayoutbuilder.lib.qobjectmaker import QObjectMaker
from qtlayoutbuilder.lib.widgetandlayoutfinder import WidgetAndLayoutFinder


class Builder(object):
    """
    This is the most fundamental and central class in the builder. It is the
    internal entry point to do almost everything to build the layouts - taking 
    as an argument one big string. It doesn't get involved in re-formatting 
    and overwriting the original file though. That is done by the client.
    """
    @classmethod
    def build(cls, one_big_string, provenance):
        # Construct the widget and layout finder helper just once and early
        # on because its construction is expensive.
        finder = WidgetAndLayoutFinder()
        layouts_created = LayoutsCreated()  # Will be populated, then returned.
        line_number = 0
        lines = MultilineString.get_as_left_shifted_lines(one_big_string)
        for line in lines:
            line_number += 1
            cls._process_line(line, finder, layouts_created, line_number,
                              provenance)
        BuilderAssertions.assert_layouts_created_is_not_empty(
                layouts_created, provenance)
        return layouts_created

    # --------------------------------------------------------
    # Private below

    @classmethod
    def _process_line(cls, line, finder, layouts_created, line_number,
                      provenance):
        """
        This function exists only to encapsulate the process_line_internals()
        function with exception handling that adds line number and input
        context to error reporting.
        """
        try:
            cls._process_line_internals(line, finder, layouts_created)
        except LayoutError as e:
            # Augment the error with line number, line contents and source.
            raise LayoutError("""
                    %s
                    (This line: <%s>)
                    (Line number: %d, from %s)
                """, (str(e), line, line_number, provenance))

    @classmethod
    def _process_line_internals(cls, line, finder, layouts_created):
        """
        The guts of the process-line logic.
        """
        is_a_comment, is_blank, indent, name, type_string, parenthesised = \
            LineParser.parse_line(line)
        if is_a_comment or is_blank:
            return

        # Amount of indentation gives us the depth at which this line lives in
        # parent-child hierarchy. Top level objects have depth=1.

        depth = 1 + indent / 2  # Integer division.
        BuilderAssertions.assert_have_not_skipped_a_level(
                depth, layouts_created)

        # Ask the QObjectMaker to create the new QObject, passing in the
        # object finder, in case it needs to find it rather than make it.
        new_qobject = QObjectMaker(finder).make(name, type_string)

        # Add then object as a child to its parent if required.
        if depth > 1:
            parent_level = depth - 1
            parent_object, parent_path = \
                layouts_created.most_recently_added_at_level(
                    parent_level)
            ChildAdder.add(new_qobject, name, parent_object)
            layouts_created.register_child(new_qobject, parent_path, name)
        else:  # A top-level object.
            layouts_created.register_top_level_object(new_qobject, name)

        # Finish up by processing any text present in the line in parenthesis.
        cls._process_parenthesised_text(parenthesised, new_qobject)

    @classmethod
    def _process_parenthesised_text(cls, parenthesised, object_to_add_text_to):
        if not parenthesised:
            return
        # We parse the parenthises text using the same function as python
        # does itself when it parses string literals in source code. This
        # means the parenthesised text can be like this: # 'hello \u25c0'.
        # In that case 25c0 is a solid left-pointing arrow.
        try:
            decoded_with_unicode_escapes = parenthesised.decode(
                'raw_unicode-escape')
        except Exception as e:
            raise LayoutError("""
                Python raised an exception when the builder tried to
                deal with unicode encoded values in your text: <%s>. The
                underlying python error was:
                %s
            """, (parenthesised, str(e)))

        # Try the text-adding methods speculatively.
        if hasattr(object_to_add_text_to, 'setText'):
            object_to_add_text_to.setText(decoded_with_unicode_escapes)
            return
        if hasattr(object_to_add_text_to, 'setTitle'):
            object_to_add_text_to.setTitle(decoded_with_unicode_escapes)
            return
        raise LayoutError("""
            Cannot do anything with the text you specified
            in parenthesis because the object being created
            has neither of the following methods: setText(), or setTitle().
            """, ())
