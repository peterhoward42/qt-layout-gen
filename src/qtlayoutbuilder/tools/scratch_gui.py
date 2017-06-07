from PyQt5.QtWidgets import qApp, QPushButton, QApplication

persist = []

if __name__ == '__main__':
    QApplication([])
    btn = QPushButton('foo')
    persist.append(btn)
    btn.show()
    qApp.exec_()
