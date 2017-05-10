"""
A program to help you while you are editing builder input files. It 
continuously monitors your file and shows you the new layout result every
time you save the file.

Usage: watch file_path

It means you can stay in an edit-review loop without having to break out to
run the builder yourself.

It reports any layout errors that are raised, but keeps monitoring.
"""

import os

from PySide.QtCore import QObject, QThread, QEvent, QCoreApplication
from PySide.QtGui import qApp, QApplication, QWidget
import sys

import qtlayoutbuilder
from qtlayoutbuilder.api.layouterror import LayoutError


class WatchApp(QObject):
    """
    The watch application. clients should instantiate it, then drop into 
    the Qt event loop.
    """

    def __init__(self, cmd_line_args):
        # The command line arguments are expected to include the input file
        # path as cmd_line_args[1].
        super(WatchApp, self).__init__()
        self._input_path = self._validate_input_path(cmd_line_args)
        self._top_level_widget = None

        # A separate thread observes when the last-modified date changes on
        # the input file, and calls back here by posting() a
        # QEvent(FileMonitor.FILE_CHANGED) back to this class' event handler.
        # (So that the monitor doesn't block the GUI thread, and all the
        # GUI code runs back here in the main thread).
        file_monitor = FileMonitorThread(self, self._input_path)
        file_monitor.start()

    def event(self, event):
        """
        Receive the FILE_CHANGED event posted from the monitor thread.
        """
        if event.type != FileMonitorThread.FILE_CHANGED:
            return
        try:
            layout = qtlayoutbuilder.api.build.build_from_file(self._input_path)
        except LayoutError as e:
            print str(e)
            return
        widget, ok = self._validate_top_level_widget(layout)
        if ok:
            if self._top_level_widget:
                self._top_level_widget.hide()
            self._top_level_widget = widget
            self._top_level_widget.show()

    def _validate_input_path(self, cmd_line_args):
        if len(cmd_line_args != 2):
            print 'Usage: watch file_path'
        return cmd_line_args[1]

    def _validate_top_level_widget(self, layout):
        item = layout.first_top_level_item()
        if isinstance(item, QWidget):
            return item, True
        return None, False


class FileMonitorThread(QThread):

    FILE_CHANGED = QEvent.User + 1 # First available non-reserved event type.

    def __init__(self, watch_app, input_path):
        self._watch_app = watch_app
        self._input_path = input_path

    def run(self):
        prev_file_time = None
        while True:
            file_time = self._get_file_time()
            if file_time != prev_file_time:
                prev_file_time = file_time
                QCoreApplication.postEvent(
                    self._watch_app, QEvent(self.FILE_CHANGED))
            sys.sleep(2.0) # Don't hog CPU.

    def _get_file_time(self):
        # If the file is being written to right now, it may be locked by
        # whatever outside party is doing so, which makes getmtime() raise
        # raise an error.
        while True:
            try:
                file_time = os.path.getmtime()
                return file_time
            except os.Error as e:
                continue


if __name__ == '__main__':
    QApplication([])
    WatchApp(sys.argv)
    qApp.exec_()

