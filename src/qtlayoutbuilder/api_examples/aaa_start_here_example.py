import sys

from PySide.QtGui import qApp, QApplication, QWidget

from qtlayoutbuilder.api.api import LayoutBuilder

if qApp is None:
    QApplication([])

layouts = LayoutBuilder.build_layouts_from_text(
    """
    VBOX:page           top_bit     bottom_bit
    HBOX:top_bit        left_bit    right_bit
    VBOX:bottom_bit     apple       pear        banana
    QLabel:left_bit
    QLabel:right_bit
    QPushButton:apple
    QPushButton:pear
    QPushButton:banana
    """
)

widget = QWidget()
top_level_layout = layouts.layout_element['page']
widget.setLayout(top_level_layout)
widget.show()

sys.exit(qApp.exec_())
