""" Foo module docstring."""

def build_layouts_from_dir(input_directory):
    records, err = _split_all_files_in_directory_into_records(input_directory)
    if err:
        return None, err.extended_with('Could not build your layouts from <%s>' % input_directory)
    return _build_layouts_from_records(records, input_directory)

def build_layouts_from_text(input_text):
    records, err = _split_text_into_records(input_text)
    if err:
        return None, err.extended_with('Could not build your layouts from <%s>' % input_text)
    return _build_layouts_from_records(records, input_text)


