import sys

from unittest import TestCase

from PySide.QtGui import qApp, QApplication, QWidget


from PySide.QtGui import QLabel, QPushButton, qApp, QApplication

from qtlayoutbuilder.api.api import LayoutBuilder

from unittest import TestCase

class TestExampleGettingStarted(TestCase):

    def test_example_getting_started(self):
        QApplication([])

        layouts = LayoutBuilder.build_layouts_from_text(
            """
            VBOX:page               top_bit bottom_bit
            HBOX:top_bit            apple pear banana orange
            HBOX:bottom_bit         foo  bar
            QLabel:apple
            QLabel:pear
            QLabel:banana
            QLabel:orange
            QPushButton:foo
            QPushButton:bar
            """
        )

        widget = QWidget()
        top_level_layout = layouts.layout_element['page']
        widget.setLayout(top_level_layout)
        widget.show()

        sys.exit(qApp.exec_())
