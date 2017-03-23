import sys

from unittest import TestCase

from PySide.QtGui import qApp, QApplication, QWidget


from PySide.QtGui import QLabel, QPushButton, qApp, QApplication

from qtlayoutbuilder.api.api import LayoutBuilder

from unittest import TestCase

class TestExampleGettingStarted(TestCase):

    def test_example_getting_started(self):
        """
        This is a very simple getting-started example, which illustrates the
        following API features:
        o  Providing the input text as a hard coded string literal in your
           program.
        o  Using shorthand keywords like VBOX to mean QVerticalBoxLayout.
        o  Adding simple Qt Widget types that don't have children (like QLabel
           and QPushButton) at the bottom level of the hierarchy.
        o  The automatated setting of the text for QLabel and QPushButton.
        o  The use of <> to add 'stretch' to box layouts.

        """
        QApplication([])

        layouts = LayoutBuilder.build_layouts_from_text(
            """
            VBOX:page               top_bit bottom_bit
            HBOX:top_bit            apple pear banana orange
            HBOX:bottom_bit         <> foo  bar
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

        qApp.exec_()
