"""
A GUI program to help you be more productive while editing builder input files.

It lets you specify an input file, and then offers a 'Build' button which
builds the layout and show()s the resultant top level widget.

Plus a 'reformat' button that reformats the input file in-place.
"""

from PySide.QtCore import QObject, QSettings
from PySide.QtGui import qApp, QApplication, QFileDialog, QLayout, QWidget, \
    QLabel

from qtlayoutbuilder.api.build import build_from_multi_line_string, \
    build_from_file
from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString

_ORG = 'PARJI'
_APP = 'QtLayoutBuilder'
_LAST_KNOWN = '_lastknown'

class HelperGui(QObject):
    """
    Speeds up the process of editing and trying out a builder input file.
    You specify your input file and then press a BUILD button any time you want.
    
    Also offers a FORMAT button that automatically reformats your input file,
    and overwrites it (in place.)
    
    Usage: Just run helper_gui.py
    """

    def __init__(self):
        super(HelperGui, self).__init__()
        self._settings = QSettings(_ORG, _APP)
        self._input_path = self._last_known_input_file()

        # Make this GUI
        self._layouts = self._make_gui()

        # Augment this GUI
        self._layouts.at('main_page').setWindowTitle('Helper GUI')
        self._layouts.at('build_btn').setToolTip(
                'Run the builder and show() the layout created.')
        self._layouts.at('format_btn').setToolTip(
                'Reformat (and overwrite the input file')

        self._set_text_for_path_label()

        # Connect signals.
        self._layouts.at('path_btn').clicked.connect(self._handle_path)
        self._layouts.at('build_btn').clicked.connect(self._handle_build)
        self._layouts.at('format_btn').clicked.connect(self._handle_reformat)

        # And show it.
        self._layouts.at('main_page').show()

    def _make_gui(self):
        layouts = build_from_multi_line_string("""
            main_page               QWidget
              page_layout           QVBoxLayout
                path_controls       QHBoxLayout
                  build_btn         QPushButton(Build)
                  path_label        QLabel(Choose input file...)
                  path_btn          QPushButton(Different File)
                  format_btn        QPushButton(Reformat)
                  stretch           QSpacerItem
                messages            QLabel(Messages show up here)
                user_content        QGridLayout
                  
        """)
        return layouts

    def _handle_path(self):
        result = QFileDialog.getOpenFileName(self._layouts.at('main_page'),
                'Choose input file', self._input_path)
        try: # PySide 1.2.4 and who knows which other?
            path, file_type_option_selected = result
        except ValueError:
            path = result # PyQt and mabye some PySide versions?
        if not path:
            return
        self._input_path = path
        # Persist the user's choice across restart.
        self._settings.setValue(_LAST_KNOWN, self._input_path)
        self._set_text_for_path_label()

    def _handle_build(self):
        try:
            users_layouts = build_from_file(
                self._input_path, auto_format_and_overwrite=False)
        except LayoutError as e:
            self._show_text_in_stack_widget(str(e))
            return
        top_item = users_layouts.first_top_level_item()
        if isinstance(top_item, QWidget):
            thing_to_show = top_item
        if isinstance(top_item, QLayout):
            wrapper = QWidget(top_item)
            thing_to_show = wrapper
        self._replace_users_layout(thing_to_show)

    def _handle_reformat(self):
        try:
            users_layouts = build_from_file(
                self._input_path, auto_format_and_overwrite=True)
            self._show_text_in_stack_widget(
                MultilineString.shift_left("""
                    Done! - You may need to refresh your editor to see the
                    formatting changes.
                """))
        except LayoutError as e:
            self._show_text_in_stack_widget(
                    "Cannot reformat the file because it won't build.")
            return

    def _last_known_input_file(self):
        last_known = self._settings.value(_LAST_KNOWN)
        if last_known:
            return last_known
        return 'Please choose an input file'

    def _set_text_for_path_label(self):
        txt = '<font color="grey">...%s</font>' % self._input_path[-30:]
        self._layouts.at('path_label').setText(txt)

    def _replace_users_layout(self, thing_to_show):
        grid = self._layouts.at('user_content')
        grid.addWidget(thing_to_show, 0, 0)

if __name__ == '__main__':
    QApplication([])
    app = HelperGui()
    qApp.exec_()

