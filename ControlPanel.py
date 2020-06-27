from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QMimeData, QByteArray, QSize)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QDrag)
from PyQt5.QtWidgets import (QGridLayout, QVBoxLayout, QHBoxLayout, QMainWindow, QAction, QActionGroup,
							QLabel, QPushButton, QButtonGroup, QDockWidget, QWidget, QSizePolicy, QMenu)
from functools import partial
from ActionButton import ActionButton
from GameLogic.MovePlanner import prePlanMove
from GameLogic.CrisisHandler import reactNews
import Local

class ControlPanel(QDockWidget):
	"""
	Main Window bottom panel - used for player interactions, consists of four panels:
	- scores panel,
	- map mode panel,
	- current selection panel,
	- turn management panel
	
	"""

	def __init__(self, parent):
		super(ControlPanel, self).__init__()
		self.parent = parent
		mainLayout = QHBoxLayout()
		multiWidget = QWidget()
		panelLayout = []
		self.titleLabel = []
		for i in range(4):
			self.titleLabel.append(QLabel())
			panelLayout.append(QGridLayout())
			mainLayout.addLayout(panelLayout[i])

		# Scores panel
		self.flagLabel = [QLabel() for i in range(2)]
		for i in range(2): self.flagLabel[i].setPixmap(parent.graphics.flag[i])
		self.scoreLabel = [QLabel() for i in range(4)]
		self.showScoreButton = QPushButton("...")
		self.showScoreButton.setFixedSize(32, 32)
		for i in range(4):
			if i < 2:
				panelLayout[0].addWidget(self.flagLabel[i], i + 1, 0)
			panelLayout[0].addWidget(self.scoreLabel[i], 1 + i % 2, 1 + i // 2)
		panelLayout[0].addWidget(self.showScoreButton, 1, 3, 1, 2)
		panelLayout[0].addWidget(self.titleLabel[0], 0, 0, 1, 4)


		# Map mode panel
		mapModeGroup = QActionGroup(self)
		self.mapModeButton = [ActionButton() for i in range(18)]
		self.mapModeAction = [QAction() for i in range(58)]
		for i in range(18):
			self.mapModeButton[i].setFixedSize(24, 24)
			self.mapModeButton[i].setIconSize(QSize(20,20))
			panelLayout[1].addWidget(self.mapModeButton[i], 1 + i // 9, i % 9)
		for i in range(58):
			self.mapModeAction[i].id = i
			self.mapModeAction[i].setCheckable(True)
			mapModeGroup.addAction(self.mapModeAction[i])
			if i < 17:
				self.mapModeButton[i].setAction(self.mapModeAction[i])
		panelLayout[1].addWidget(self.titleLabel[1], 0, 0, 1, 9)
		self.mapModeButton[17].setEnabled(False)
		
		# Selection panel
		self.selectionFlag = QLabel()
		self.selectionInfo = [QLabel() for i in range(2)]
		self.closeUpButton = QPushButton(parent.graphics.icon[20], "")
		self.newsButton = QPushButton(parent.graphics.icon[22], "")
		for i,j in zip((self.selectionFlag, self.selectionInfo[0], self.closeUpButton, self.newsButton), range(4)):
			panelLayout[2].addWidget(i, 1, j)
			if isinstance(i, QPushButton):
				i.setFixedSize(32, 32)
				i.setIconSize(QSize(30,30))
		panelLayout[2].addWidget(self.selectionInfo[1], 2, 1)
		panelLayout[2].addWidget(self.titleLabel[2], 0, 0, 1, 4)
		for i in range(2):
			self.selectionInfo[i].setFixedWidth(150)

		# Year label
		self.yearLabel = QLabel("1982")
		#self.yearLabel.setAlignment = Qt.AlignCenter
		self.switchPlayerButton = QPushButton("Switch\nplayer")
		self.nextTurnButton = QPushButton("Next\nturn")
		panelLayout[3].addWidget(self.yearLabel, 1, 0, 1, 2)
		for i,j in zip((self.switchPlayerButton, self.nextTurnButton), range(2)):
			panelLayout[3].addWidget(i, 2, j)
			i.setFixedWidth(70)
			i.setFixedHeight(35)
		panelLayout[3].addWidget(self.titleLabel[3], 0, 0, 1, 2)

		#stretch labels
		for i in (self.titleLabel + [self.yearLabel]):
			i.setAlignment(Qt.AlignCenter)
		self.setTitleBarWidget(QWidget())
		multiWidget.setLayout(mainLayout)
		self.setWidget(multiWidget)
		self.setFixedHeight(92)
		self.setStrings()

	def setStrings(self):
		self.updatePlayerNames()
		for i in range(4):
			self.titleLabel[i].setText("<b>"+Local.strings[Local.MAIN_PANEL][4 + i]+"</b>")
		self.switchPlayerButton.setText(Local.strings[Local.MAIN_PANEL][8])
		self.nextTurnButton.setText(Local.strings[Local.MAIN_PANEL][9])
		for i in range(58):
			if i < 17:
				self.mapModeAction[i].setIcon(self.parent.graphics.icon[i])
				self.mapModeAction[i].setText(Local.strings[Local.MENU][i])
			elif 17 <= i <= 21:
				self.mapModeAction[i].setIcon(self.parent.graphics.icon[i - 9])
				self.mapModeAction[i].setText(Local.strings[Local.MENU][i - 9])
			elif 24 <= i <= 32:
				self.mapModeAction[i].setText(Local.strings[Local.MENU][i % 3 + 17])
			elif 22 <= i <= 23:
				self.mapModeAction[i].setText(Local.strings[Local.MENU][i - 5])
			elif 32 <= i <= 34:
				self.mapModeAction[i].setText(Local.strings[Local.MENU][i - 13])
			else: self.mapModeAction[i].setText(Local.strings[Local.MENU][i - 4])

	def connectActions(self):
		for i in range(58):
			self.mapModeAction[i].triggered.connect(partial(self.parent.mapView.setMapMode, i))
		self.newsButton.released.connect(self.parent.newsWindow.showUp)
		self.showScoreButton.released.connect(self.parent.scoresWindow.show)
		self.switchPlayerButton.released.connect(self.doChangeSides)
		self.nextTurnButton.released.connect(self.doNextTurn)

	def updateSelection(self):
		selection = self.parent.mapView.selection
		if selection:
			self.selectionFlag.setPixmap(self.parent.graphics.flag[selection.id])
			self.selectionInfo[0].setText(Local.strings[Local.DATA_COUNTRIES + selection.id][Local.CTRY_NAME])
			self.selectionInfo[1].setText(selection.value)
		else:
			self.selectionFlag.setPixmap(self.parent.graphics.emptyFlag)
			self.selectionInfo[0].setText(Local.strings[Local.MAIN_PANEL][24])
			self.selectionInfo[1].setText("")
		self.closeUpButton.setEnabled(selection != None)

	def updatePlayerNames(self):
		"""Update superpower names in the leftmost panel."""
		for i in range(2):
			label = Local.strings[Local.DATA_COUNTRIES + i][Local.CTRY_NAME]
			if i == self.parent.world.human: label += Local.strings[Local.MAIN_PANEL][10]
			if i == self.parent.world.cmptr and not self.parent.world.twoPFlag:
				label += Local.strings[Local.MAIN_PANEL][11]
			self.scoreLabel[i].setText(label)

	def drawScores(self):
		"""Update scores on the control panel"""
		for i,c in zip(range(2), self.parent.world.country[:2]):
			self.scoreLabel[i+2].setText(str(c.score - c.initScore))
		# And also, on the Scores Window
		self.parent.scoresWindow.update()

	def doChangeSides(self):
		"""Action performed on releasing 'Switch player' button"""
		self.parent.world.changeSides()
		self.parent.setStatus(-1)
		self.nextTurnButton.setEnabled(True)
		self.updatePlayerNames()

	def doNextTurn(self):
		"""Action performed on releasing 'Next turn' button"""
		self.nextTurnButton.setEnabled(False)
		prePlanMove(self.parent.world)
		reactNews(self.parent, self.parent.world)
		
