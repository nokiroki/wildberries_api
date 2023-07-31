import sys

from PyQt5 import QtWidgets

from mainwindow import MainWindow


app = QtWidgets.QApplication([])
window = MainWindow()
window.show()

sys.exit(app.exec())
