from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLabel, QWidget, QDockWidget, QToolBar, QSizePolicy)

class StatusBar(QDockWidget):

    def __init__(self, parent):
        super(StatusBar, self).__init__()
        self.label = QLabel()
        #self.label.setFixedWidth(parent.width() - 10)
        self.setTitleBarWidget(QWidget())
        self.setStyleSheet("background-color:white; border: 1px solid lightgray;")
        self.layout().setContentsMargins(0,0,0,0)
        self.setLabel("Your turn")
        #spacer = QWidget()
        #spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.setMovable(False)
        #self.setFloatable(False)
        #self.addWidget(spacer)
        self.setWidget(self.label)
        self.setFixedHeight(20)

    def setLabel(self, text):
        self.label.setText("<p align='center'><h3>" + text + "</h3></p>")