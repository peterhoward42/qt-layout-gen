"""
A GUI program to help you be more productive while editing builder input files.

It lets you specify an input file, and then offers a 'Build' button which
builds the layout and show()s the resultant top level widget.

Plus a 'reformat' button that reformats the input file in-place.
"""

from PySide.QtCore import QObject, QSettings
from PySide.QtGui import qApp, QApplication, QFileDialog, QLayout

from qtlayoutbuilder.api.build import build_from_multi_line_string, \
    build_from_file
from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString

_ORG = 'PARJI'
_APP = 'QtLayoutBuilder'
_LAST_KNOWN = '_lastknown'
_DEFAULT_PATH = 'no_such_dir/no_such_file.txt'

class BuilderGui(QObject):
    """
    The watch application. clients should instantiate it, then drop into 
    the Qt event loop.
    """

    def __init__(self):
        super(BuilderGui, self).__init__()
        self._last_user_widget_shown = None
        self._settings = QSettings(_ORG, _APP)

        self._input_path = self._last_known_input_file()

        self._layouts = self._make_gui()

        self._layouts.at('path_label').setText(self._input_path)

        self._layouts.at('path_btn').clicked.connect(self._handle_path)
        self._layouts.at('build_btn').clicked.connect(self._handle_build)
        self._layouts.at('format_btn').clicked.connect(self._handle_reformat)

        self._layouts.at('main_page').show()

    def _make_gui(self):
        layouts = build_from_multi_line_string("""
            main_page               QWidget
              page_layout           QVBoxLayout
                path_controls       QHBoxLayout
                  path_label        QLabel(Choose input file...)
                  path_btn          QPushButton(Choose)
                main_btns           QHBoxLayout
                  build_btn         QPushButton(Build)
                  format_btn        QPushButton(Reformat)
                log_pane            QTextEdit
        """)
        return layouts

    def _handle_path(self):
        path = QFileDialog.getOpenFileName(
            None, 'Input file', self._input_path, 'Text files (*.txt)')
        self._input_path = path
        #self._settings.setValue(_LAST_KNOWN, self._input_path)
        self._layouts.at('foo').setText(self._input_path)

    def _handle_build(self):
        try:
            users_layouts = build_from_file(
                self._input_path, auto_format_and_overwrite=False)
        except LayoutError as e:
            self._layouts.at('foo').setText(str(e))
            return
        top_item = users_layouts.get_first_top_level()
        if isinstance(top_item, QLayout):
            self._users_layouts.at('foo').setText(
                MultilineString.shift_left("""
                    Your top level item is a QLayout, so I cannot
                    show() it. If you wrap your layout in a QWidget,
                    then I can.
                """))
        else:
            if self._last_user_widget_shown:
                self._last_user_widget_shown.hide()
            self._last_user_widget_shown = top_item
            self._last_user_widget_shown.show()
            self._users_layouts.at('foo').setText('Done')

    def _handle_reformat(self):
        try:
            users_layouts = build_from_file(
                self._input_path, auto_format_and_overwrite=True)
            self._users_layouts.at('foo').setText(
                MultilineString.shift_left("""
                    Your input file has been reformatted and overwritten.
                    You may need to reload it to see the changes in your
                    editor.
                """))
        except LayoutError as e:
            self._layouts.at('foo').setText(str(e))
            return

    def _last_known_input_file(self):
        """
        last_known = self._settings.value(_LAST_KNOWN)
        if last_known:
            return last_known
        """
        return _DEFAULT_PATH # splittable default



if __name__ == '__main__':
    QApplication([])
    app = BuilderGui()
    qApp.exec_()

