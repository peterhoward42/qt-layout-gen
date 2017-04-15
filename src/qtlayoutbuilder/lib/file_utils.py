from qtlayoutbuilder.api.layouterror import LayoutError


def get_file_contents_as_a_string(file_path):
    try:
        with open(file_path, 'r') as my_file:
            return my_file.read()
    except Exception as e:
        raise LayoutError("""
            Cannot read this file: <%s>.
            The underlying error reported is: %s.
        """, (file_path, str(e)))
