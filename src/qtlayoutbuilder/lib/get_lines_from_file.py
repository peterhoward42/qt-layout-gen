from qtlayoutbuilder.api_orig.layouterror import LayoutError


def get_lines_from_file(file_path):
    try:
        with open(file_path, 'r') as my_file:
            lines = my_file.readlines()
            return lines
    except Exception as e:
        raise LayoutError(str(e), None)
