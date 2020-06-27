from PyQt5.QtWidgets import (QGridLayout, QBoxLayout, QHBoxLayout, QMainWindow,
							QLabel, QRadioButton, QPushButton, QGroupBox, QDialog, QButtonGroup)
from GameLogic.World import World
from GameLogic.MovePlanner import prePlanMove, mainMove
import Local

class NewGameWindow(QDialog):

    def __init__(self, parent):
        super(NewGameWindow, self).__init__(parent)
        self.parent = parent
        self.buttonGroups = [QButtonGroup() for i in range(3)]
        mainLayout = QBoxLayout(QBoxLayout.TopToBottom)
        columnLayout = QBoxLayout(QBoxLayout.LeftToRight)
        buttonLayout = QBoxLayout(QBoxLayout.LeftToRight)
        column = [QBoxLayout(QBoxLayout.TopToBottom) for i in range(3)]
        level = QGroupBox("Level of play")
        self.levelOpt = [QRadioButton(str(i)) for i in range(4)]
        for i in self.levelOpt:column[0].addWidget(i)
        side = QGroupBox("Side to play")
        mode = QGroupBox("Number of players")
        self.sideOpt = [QRadioButton(str(i)) for i in range(2)]
        self.modeOpt = [QRadioButton(str(i)) for i in range(2)]
        for i,j in zip(self.sideOpt, self.modeOpt):
            column[1].addWidget(i)
            column[2].addWidget(j)
        for i,col in zip( (level, side, mode), column):
            i.setLayout(col)
            columnLayout.addWidget(i)
        for i,j in zip(self.levelOpt, range(4)):
            self.buttonGroups[0].addButton(i,j)
        for i,k,j in zip(self.sideOpt, self.modeOpt, range(2)):
            self.buttonGroups[1].addButton(i,j)
            self.buttonGroups[2].addButton(k,j)
        
        self.topText = QLabel("Your goal in this game is to increase the geopolitical prestige of your chosen superpower" + 
                          " while avoiding a nuclear war. The four levels provide increasingly complex and accurate representations" +
                          " of the real world of geopolitics.")
        self.topText.setWordWrap(True)
        cancel = QPushButton("Cancel")
        cancel.released.connect(self.close)
        accept = QPushButton("OK")
        accept.released.connect(self.doSetNewGame)
        buttonLayout.addWidget(cancel)
        buttonLayout.addWidget(accept)
        mainLayout.addWidget(self.topText)
        mainLayout.addLayout(columnLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        self.setFixedSize(400, 310)
        self.setModal(True)
        self.setStrings()

    def doSetNewGame(self):
        """Action performed on releasing the 'OK' button"""
        self.parent.saveOptions()
        level = self.buttonGroups[0].checkedId() + 1
        side = self.buttonGroups[1].checkedId()
        mode = (self.buttonGroups[2].checkedId() == 1)
        self.parent.controlPanel.switchPlayerButton.setEnabled(mode)
        self.parent.setStatus(25)
        self.close()
        painter = self.parent.mapView.scene().mapPainter
        # Set the new world
        self.parent.setWorld(World(level, mode, side))
        # Execute the first part of the first turn
        prePlanMove(self.parent.world)
        mainMove(self.parent, self.parent.world)
        self.parent.setStatus(-1)
        self.parent.controlPanel.drawScores()
        painter.recalculateMapBuffer()
        self.parent.mapView.resetMapView()
        print([c.getInsurgency() for c in self.parent.world.country])


    def setStrings(self):
        g = Local.WINDOW_NEWGAME
        for i in range(2):
            self.sideOpt[i].setText(Local.strings[g][i + 4])
            self.modeOpt[i].setText(Local.strings[g][i + 6])
        for i in range(4):
            self.levelOpt[i].setText(Local.strings[g][i])
        self.topText.setText(Local.strings[g][11])
        self.setWindowTitle(Local.strings[g][12])