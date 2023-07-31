import typing
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget

from design import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
