from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QIcon)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
							QGridLayout, QVBoxLayout, QHBoxLayout, QMainWindow,
							QLabel, QLineEdit, QPushButton, QSpinBox, QStyleFactory, QAction, QActionGroup)
from GameLogic.World import World
from MapView import MapView
from ControlPanel import ControlPanel
from GraphicsLoader import Graphics
from StatusBar import StatusBar
from Dialog.NewGameWindow import NewGameWindow
from Dialog.PolicyWindow import PolicyWindow
from Dialog.NewsWindow import NewsWindow
from Dialog.CloseUpWindow import CloseUpWindow
from Dialog.ScoresWindow import ScoresWindow
from Dialog.LostGameWindow import LostGameWindow
from Menu import Menu
from constants import DEFAULT_OPTS, INAVL_MAP_MODES
import json
import time
import pickle
import Local
from functools import partial

class MainWindow(QMainWindow):
	def __init__(self,parent):
		super(MainWindow, self).__init__()
		self.graphics = Graphics()
		self.parent = parent
		self.setFixedSize(950,631)
		self.setWindowTitle("Balance of Power")
		self.setStyleSheet("QMainWindow::separator{ width: 0px; height: 0px, margin: -10px; }")
		self.world = World(4,False,0)
		self.policyWindow = PolicyWindow(self)
		self.mapView = MapView(self, self.world)
		self.statusBar = StatusBar(self)
		self.newGameWindow = NewGameWindow(self)
		self.newsWindow = NewsWindow(self)
		self.closeUpWindow = CloseUpWindow(self)
		self.scoresWindow = ScoresWindow(self)
		self.controlPanel = ControlPanel(self)
		self.lostGameWindow = LostGameWindow(self)
		for i in range(2,80,1):
			self.world.addNews(self.world.country[1], self.world.country[i], self.world.country[i], 2 + i%4, 1, 2, False)
		self.addDockWidget(Qt.BottomDockWidgetArea, self.controlPanel)
		self.addDockWidget(Qt.TopDockWidgetArea, self.statusBar)
		self.setCentralWidget(self.mapView)
		self.setWindowIcon(QIcon(self.graphics.progIcon))
		self.controlPanel.connectActions()
		self.menu = Menu(self)
		self.setMenuBar(self.menu)
		self.loadOptions()
		self.mapView.resetMapView()

	def loadOptions(self):
		try:
			with open("options.dat", "r") as f:
				options = json.load(f)
		except: options = DEFAULT_OPTS
		for i,j in zip(options[:3], self.menu.options[:3]):
			j.setChecked(i)
		self.newGameWindow.levelOpt[options[4]].setChecked(True)
		self.newGameWindow.modeOpt[options[5]].setChecked(True)
		self.newGameWindow.sideOpt[options[6]].setChecked(True)
		self.menu.languages[options[3]].setChecked(True)

	def saveOptions(self):
		options = [i.isChecked() for i in self.menu.options[:3]]
		for i in self.menu.languages.values():
			if i.isChecked():
				options += [i.text().lower() + ".json"]
				break
		options += [i.checkedId() for i in self.newGameWindow.buttonGroups]
		try:
			with open("options.dat", "w") as f:
				json.dump(options, f)
		except: pass

	def updateLevel(self):
		for i in INAVL_MAP_MODES[self.world.level - 1]:
			self.controlPanel.mapModeAction[i].setEnabled(False)
			self.controlPanel.mapModeButton[i].setEnabled(False)

	def setStatus(self, id):
		"""Set status label in the top part of the window"""
		# if -1, set currently moving player
		if id == -1:
			if self.world.twoPFlag:
				self.statusBar.setLabel(Local.strings[Local.MAIN_PANEL][15] \
				 	+ Local.strings[Local.DATA_COUNTRIES + self.world.human][Local.CTRY_NAME])
			else: self.statusBar.setLabel(Local.strings[Local.MAIN_PANEL][14])
		else: self.statusBar.setLabel(Local.strings[Local.MAIN_PANEL][id])
		time.sleep(.1)
		QApplication.processEvents()

	def endGame(self):
		"""Show effects of the game ending, depends on the active flag"""
		status = 0
		if self.world.winFlag:
			self.scoresWindow.setVisible(True)
			status = 27
		elif self.world.ANWFlag or self.world.NWFlag:
			self.lostGameWindow.showUp(self.world.ANWFlag)
			status = 28
		self.setStatus(status)

	def saveWorld(self):
		"""Save the self.world property into the save.dat file using the pickle protocol"""
		print("SAVE")
		try: pickle.dump(self.world, open("save.dat", "wb"))
		except: print("ERROR SAVING")

	def loadWorld(self):
		"""Load the pickled save.dat file into the self.world property"""
		try:
			self.world = pickle.load(open("save.dat", "rb"))
			self.setStatus(-1)
			self.controlPanel.drawScores()		
			self.mapView.scene().mapPainter.recalculateMapBuffer()
			self.mapView.resetMapView()
		except: print("ERROR LOADING")

	def setWorld(self, newWorld):
		"""Set the self.world property"""
		# Backup old graphics polygons items
		polys = [c.mapPolyObject for c in self.world.country]
		# Make sure all the data are cleared
		try: del self.world
		except: pass
		# Create the new world
		self.world = newWorld
		self.mapView.scene().mapPainter.setWorld(self.world)
		self.updateLevel()
		# Move old graphics polygons onto the new world
		for poly,cntry in zip(polys, self.world.country):
			cntry.mapPolyObject = poly

if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	#print(QStyleFactory.keys())
	#app.setStyle(QStyleFactory.keys()[0])
	mainWindow = MainWindow(app)
	mainWindow.show()

sys.exit(app.exec_())