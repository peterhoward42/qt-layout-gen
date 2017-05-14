"""
A tool that aims to make it quicker and easier to iterate on developing your
input files, by providing immediate feedback with no extra programming effort.

It listens out for every change you make to your input file shows you 
immediately what your GUI looks like.

It also offers a REFORMAT button that reformats your input file in place.

Usage: Just run helper_gui.py
"""
import os

from PySide.QtCore import QObject, QSettings, QTimer, QPoint
from PySide.QtGui import qApp, QApplication, QFileDialog, QLayout, QWidget, \
    QMessageBox

from qtlayoutbuilder.api.build import build_from_multi_line_string, \
    build_from_file
from qtlayoutbuilder.api.layouterror import LayoutError
from qtlayoutbuilder.lib.multiline_string_utils import MultilineString

_ORG = 'PARJI'
_APP = 'QtLayoutBuilder'
_LAST_KNOWN = '_lastknown'

class HelperGui(QObject):

    def __init__(self):
        super(HelperGui, self).__init__()
        self._settings = QSettings(_ORG, _APP)
        self._input_path = self._last_known_input_file()
        self._last_shown_content = None
        self._previous_timestamp = None

        # Make this GUI
        self._layouts = self._make_gui()

        # Capture the GUI items we need to interact with programmatically.
        # (Avoids proliferation of string literals and aids testing).
        self._main_page = self._layouts.at('main_page')
        self._format_btn = self._layouts.at('format_btn')
        self._path_btn = self._layouts.at('path_btn')
        self._log = self._layouts.at('log')
        self._path_label = self._layouts.at('path_label')

        # Augment this GUI
        self._main_page.setWindowTitle('QtLayoutBuilder Helper GUI')
        self._format_btn.setToolTip('Reformat (and overwrite the input file)')
        self._set_text_for_path_label()

        # Connect signals.
        self._path_btn.clicked.connect(self._handle_path)
        self._format_btn.clicked.connect(self._handle_reformat)

        # And show it.
        self._main_page.show()

        # Set up the timed call back to see if the input file has changed.
        self._timer = QTimer()
        self._timer.timeout.connect(self._timer_callback)
        self._timer.start(500) # milli-seconds

    def _make_gui(self):
        layouts = build_from_multi_line_string("""
            main_page               QWidget
              page_layout           QVBoxLayout
                path_controls       QHBoxLayout
                  path_label        QLabel(Choose input file...)
                  path_btn          QPushButton(Choose File)
                  format_btn        QPushButton(Reformat)
                log_groupbox        QGroupBox(Log)
                  log_layout        QVBoxLayout
                    log                 QLabel(Messages show up here)
                  
        """)
        return layouts


    #-------------------------------------------------------------------------
    # Event handlers

    def _handle_path(self):
        result = QFileDialog.getOpenFileName(self._main_page,
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

    def _handle_reformat(self):
        try:
            users_layouts = build_from_file(
                    self._input_path, auto_format_and_overwrite=True)
            # We should provide some confirmation and feedback. The log is
            # not much good because the overwrite stimualtes a fresh build
            # which almost immediately replaces any log message we put out here.
            QMessageBox.information(self._main_page,
                '', 'Reformat Done\n\n+ Original file overwritten.')
        except LayoutError as e:
            self._log.setText("Cannot reformat the file because it won't build.")
            return

    def _timer_callback(self):
        if self._file_has_been_updated():
            self._attempt_build()

    #-------------------------------------------------------------------------
    # Utility helpers

    def _file_has_been_updated(self):
        # Returns True if the input file's timestamp has changed from
        # last time we got a measurement.

        # The call to time.getmtime() will raise exceptions if the file
        # is temporarily locked (maybe by the editor doing a save), so when
        # this is so, we just it hasn't changed, and wait for the next timer
        # tick. This does mean that if the file has really gone missing we
        # will not detect it, but better to avoid the complexity of two
        # timers or similar.
        if self._input_path is None:
            return False
        try:
            mtime = os.path.getmtime(self._input_path)
            if mtime != self._previous_timestamp:
                self._previous_timestamp = mtime
                return True
        except Exception as e: # Can be IOError or WindowsError or ?
            return False

    def _attempt_build(self):
        try:
            users_layouts = build_from_file(self._input_path,
                    auto_format_and_overwrite = False)
        except LayoutError as e:
            if 'Cannot read this file' in str(e):
                self._log.setText(MultilineString.shift_left("""
                    The builder says it cannot access your input file,
                    but that is probably because your editor had it locked
                    at the moment it tried. It will carry on as normal the
                    next time you save a change.
                """))
            else:
                self._log.setText(str(e))
            return
        top_item = users_layouts.first_top_level_item()
        if isinstance(top_item, QWidget):
            thing_to_show = top_item
        if isinstance(top_item, QLayout):
            wrapper = QWidget(top_item)
            thing_to_show = wrapper
        self._show_built_content(thing_to_show)
        self._log.setText('Build successful')

    def _last_known_input_file(self):
        last_known = self._settings.value(_LAST_KNOWN)
        if last_known:
            return last_known
        return None

    def _set_text_for_path_label(self):
        if self._input_path is None:
            self._path_label.setText(
                '<font color="red">Please choose input file</font>'
            )
        else:
            self._path_label.setText(
                '<font color="grey">...%s</font>' % self._input_path[-30:]
        )

    def _show_built_content(self, thing_to_show):
        if self._last_shown_content is not None:
            self._last_shown_content.hide()
        self._last_shown_content = thing_to_show
        thing_to_show.move(QPoint(0,0))
        self._last_shown_content.show()

if __name__ == '__main__':
    QApplication([])
    app = HelperGui()
    qApp.exec_()

