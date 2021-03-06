from qtlayoutbuilder.api.layouterror import LayoutError


class BuilderAssertions(object):
    """
    A set of assertion functions that the builder can use which raise
    properly formed LayoutError(s) when the assertions are false.
    """

    @classmethod
    def assert_multiple_of_two(cls, indent):
        if indent % 2 == 0:
            return
        raise LayoutError("""
            A line is indented by %d spaces.
            Indentation spaces must be a multiple of 2.
            """, indent)

    @classmethod
    def assert_have_not_skipped_a_level(cls, level, layouts_created):
        # Only allowed to descend levels in single steps.
        if level <= layouts_created.current_level() + 1:
            return
        raise LayoutError("""
            This line is indented too much.
            It cannot be indented relative to the line
            above it by more than 2 spaces.
        """, ())

    @classmethod
    def assert_layouts_created_is_not_empty(cls, layouts_created, provenance):
        if layouts_created.is_empty():
            raise LayoutError("""
                This input provided (%s) contains nothing, or
                nothing except whitespace and comments.
                """, provenance)

    @classmethod
    def assert_no_tabs_present(cls, line):
        if '\t' not in line:
            return
        raise LayoutError("""
            This line contains a tab character - which is not allowed.
            """, ())
