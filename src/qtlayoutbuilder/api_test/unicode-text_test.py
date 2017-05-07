import os
from unittest import TestCase

from PySide.QtGui import QApplication, qApp, QLabel

from qtlayoutbuilder.api.build import build_from_multi_line_string


class TestUnicodeText(TestCase):
    """
    This class exercies the builder with a large variety of Qt widget and
    layout types.
    """

    @classmethod
    def setUpClass(cls):
        # Needs QApplication context.
        super(TestUnicodeText, cls).setUpClass()
        try:
            QApplication([])
        except RuntimeError:
            pass  # Singleton already exists

    def test_unicode_text(self):
        layouts_created = build_from_multi_line_string("""
            page          QWidget
              layout      QVBoxLayout
                layout1   QHBoxLayout
                  btn1    QPushButton(\u2605)
                  btn2    QPushButton(\u2605)
                  btna    QToolButton(\u2791)
                  btnb    QToolButton(\u2791)
                  btnc    QToolButton(\u2791)
                  label1  QLabel(\u2791)
                  label2  QLabel(\u2791)
        """)

        widget = layouts_created.get_element('page')
        widget.setStyleSheet("""
            * {
            font-family: Lucida Sans Unicode;
            font-size: 25px;
            }
        """)
        widget.show()
        qApp.exec_()

