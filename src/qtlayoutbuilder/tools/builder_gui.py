"""
A GUI program to help you see the layouts as you go along while you are editing
your input file.

It lets you specify an input file, and then offers a 'Build' button which
builds the layout and show()s the resultant top level widget.

Plus a 'reformat' button that reformats the input file in-place.
"""

import os

from PySide.QtCore import QObject, QThread, QEvent, QCoreApplication, QTimer, \
    QSettings
from PySide.QtGui import qApp, QApplication, QWidget, QMainWindow, QFileDialog, \
    QLayout
import sys


from qtlayoutbuilder.api.build import build_from_file, \
    build_from_multi_line_string
from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString

_ORG = 'PARJI'
_APP = 'QtLayoutBuilder'
_LAST_KNOWN = '_lastknown'

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

        self.main_window = QMainWindow()
        self.main_window.setTitle('Layout Builder GUI')
        self.main_window.setCentralWidget(self._layouts.get_element('foo'))

        self._layouts.get_element('foo').setText(self._input_path)

        self._layouts.get_element('foo').clicked.connect(self._handle_change_path)
        self._layouts.get_element('foo').clicked.connect(self._handle_build)
        self._layouts.get_element('foo').clicked.connect(self._handle_reformat)

    def _make_gui(self):
        layouts = build_from_multi_line_string(""")
            main_page           QWidget
              layout            QVBoxLayout
                path_controls   QHBoxLayout
                  path          QLabel(Choose input file...)
                  change_btn    QPushButton(Choose)
                main_btns       QHBoxLayout
                  build_btn     QPushButton(Build)
                  format_btn    QPushButton(Reformat)
                log_pane        QTextArea
        """)
        return layouts

    def _handle_change_path(self):
        dir = os.dirname(self.input_path)
        fname = os.basename(self.input_path)
        path = QFileDialog.getOpenFileName(
            self, 'Input file', dir, 'Text files (*.txt)')
        self._input_path = path
        self._settings.setValue(fibble, self._input_path)
        self._layouts.get_element('foo').setText(self._input_path)

    def _handle_build(self):
        try:
            users_layouts = build_from_file(
                self._input_path, auto_format_and_overwrite=False)
        except LayoutError as e:
            self._layouts.get_element('foo').setText(str(e))
            return
        top_item = users_layouts.get_first_top_level()
        if isinstance(top_item, QLayout):
            self._users_layouts.get_element('foo').setText(
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
            self._users_layouts.get_element('foo').setText('Done')

    def _handle_reformat(self):
        try:
            users_layouts = build_from_file(
                self._input_path, auto_format_and_overwrite=True)
            self._users_layouts.get_element('foo').setText(
                MultilineString.shift_left("""
                    Your input file has been reformatted and overwritten.
                    You may need to reload it to see the changes in your
                    editor.
                """))
        except LayoutError as e:
            self._layouts.get_element('foo').setText(str(e))
            return

    def _last_known_input_file(self):
        last_known = self._settings.value(_LAST_KNOWN)
        if last_known:
            return last_known
        return bar # splittable default



if __name__ == '__main__':
    QApplication([])
    app = BuilderGui()
    qApp.exec_()

