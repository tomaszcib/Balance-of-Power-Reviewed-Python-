from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGridLayout, QBoxLayout, QHBoxLayout,
							QLabel, QPushButton, QDialog)
import Local

class LostGameWindow(QDialog):

    def __init__(self, parent):
        super(LostGameWindow, self).__init__(parent)
        mainLayout = QBoxLayout(QBoxLayout.TopToBottom)
        mainLayout.setAlignment(Qt.AlignCenter)
        self.quitButton = QPushButton("<font color=\"white\">OK</font>")
        self.quitButton.released.connect(self.hide)
        self.text = QLabel("Lorem ipsum dolor sit amet")
        self.text.setWordWrap(True)
        self.setStyleSheet("background-color: black;")
        mainLayout.addWidget(self.text)
        mainLayout.addWidget(self.quitButton)
        self.setLayout(mainLayout)
        self.setFixedSize(400, 300)
    
    def showUp(self, accidental):
        str = "<font color=\"white\"><p align=\"center\">%s<br><br></p></font>" % \
            (Local.strings[Local.WINDOW_ENDGAME][0] % \
                Local.strings[Local.WINDOW_ENDGAME][2 if accidental else 1])
        self.text.setText(str)
        self.setVisible(True)
