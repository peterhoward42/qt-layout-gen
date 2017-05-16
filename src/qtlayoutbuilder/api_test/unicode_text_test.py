from unittest import TestCase

from PySide.QtGui import QApplication, qApp

from qtlayoutbuilder.api.build import build_from_multi_line_string


class TestUnicodeText(TestCase):
    """
    Exercies the builder with a variety of Unicode symbols on buttons.
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
                          # left arrow
                  btn1    QPushButton(\u25c0)
                          # right arrow
                  btn2    QPushButton(\u25b6)
                          # envelope
                  btna    QToolButton(\u2709)
                          # pencil
                  btnb    QToolButton(\u270e)
                          # hamburger
                  btnc    QToolButton(\u2630)
                          # return / enter
                label1  QLabel(Press \u23ce when done.)
        """)

        widget = layouts_created.at('page')
        widget.setStyleSheet(""" * { font-size: 36px; } """)
        widget.show()
        #qApp.exec_()
