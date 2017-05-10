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

from PySide.QtCore import QObject, QThread, QEvent, QCoreApplication, QTimer
from PySide.QtGui import qApp, QApplication, QWidget
import sys


from qtlayoutbuilder.api.build import build_from_file
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
        self._prev_contents = None

        self._timer = QTimer()
        self._timer.timeout.connect(self._timer_callback)
        self._timer.start(2.0)

    def _timer_callback(self):
        # Only react when the file contents have changed.
        new_contents = self._get_file_contents()
        if new_contents == self._prev_contents:
            return
        self._prev_contents = new_contents
        try:
            layout = build_from_file(self._input_path)
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
        if len(cmd_line_args) != 2:
            print 'Usage: watch file_path'
        return cmd_line_args[1]

    def _validate_top_level_widget(self, layout):
        item = layout.first_top_level_item()
        if isinstance(item, QWidget):
            return item, True
        return None, False

    def _get_file_contents(self):
        # Loop to cope with access errors arising from another process writing
        # to the file.
        while True:
            try:
                with open(self._input_path, 'r') as input_file:
                    return input_file.read()
            except IOError as e:
                continue

if __name__ == '__main__':
    QApplication([])
    app = WatchApp(sys.argv)
    qApp.exec_()

