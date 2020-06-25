from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QPoint, QTimeLine, QPointF, QEvent)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QPixmap, QPolygonF, QPainterPath, QBrush, QTransform,
                            QIcon, QFontMetrics, QCursor)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsPolygonItem, QGraphicsItem,
							QGridLayout, QVBoxLayout, QHBoxLayout, QMainWindow, QSizePolicy,
							QLabel, QLineEdit, QPushButton, QSpinBox, QWidget, QToolTip, QMenu, QAction, QProgressBar)
from MapPainter import MapPainter
from MapCountryPolygon import MapCountryPolygon
import json
from constants import *
import Local
from functools import partial


class MapScene(QGraphicsScene):
    pixmap = None
    img = None
    mapBytes = None

    def __init__(self, parent, world):
        super(MapScene, self).__init__()
        self.parent = parent
        self.mapPainter = MapPainter(parent, world)
        self.pixmap = QPixmap("img/background.png")
        self.pixmap = self.addPixmap(self.pixmap)
        self.initCountryPolygons(world)
        self.update()

    def initCountryPolygons(self, world):
        # Load polygons from json file
        with open("data/map_data.json", "r") as f:
            polygons = json.load(f)
        for poly in polygons:
            id, x, y, compass = poly["country_id"] - 1, poly["x"], poly["y"] - 32, poly["compass"]
            c = world.country[id]
            pts = [QPointF(x,y)]
            k = 0
            while k < len(compass):
                if 48 <= ord(compass[k]) <= 57:
                    delta, k = int(compass[k]), k + 1
                else: delta = 1
                if compass[k] == 'n': y -= delta
                elif compass[k] == 's': y += delta
                elif compass[k] == 'e': x += delta
                elif compass[k] == 'w': x -= delta
                pts.append(QPointF(x,y))
                k += 1
            # Store graphical QGrapicsPolygonItem objects inside MapCountryPolygon object
            # MapCountryPolygon object is kept in parenting Country object
            if c.mapPolyObject == None:
                c.mapPolyObject = MapCountryPolygon(self, c.id, QPolygonF(pts))
            else: c.mapPolyObject.addPolygon(c.id, QPolygonF(pts))

class LegendLabel(QLabel):
    """
    Widget containing legend for the current map mode.
    The `button` argument is a QPushButton item inside a MapView object.

    """
    def __init__(self, parent, button, title, colors, captions):
        super(LegendLabel, self).__init__(parent)
        self.envokingButton = button
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        if len(colors) > 0:
            self.setLegend(title, colors, captions)
        self.setVisible(False)
    
    def setLegend(self, title, colors, captions):
        """
        Set legend. Colors and captions are iterables of the same length.

        """
        fm = QFontMetrics(self.font())
        self.legendText = "<b>%s</b><table>" % (title)
        tipHeight = len(captions) * (fm.height() + 4)
        captionsLen = [len(i) for i in captions]
        tipWidth = fm.width(captions[captionsLen.index(max(captionsLen))] + " " * 10)
        self.tipSize = QPoint(tipWidth, tipHeight)
        for i,j in zip(colors, captions):
            self.legendText += ("<tr><td bgcolor=%s>%s</td><td> %s</td></tr>" % (i.name(), "&nbsp;" * 5, j))
        self.legendText += "</table>"
        self.setText(self.legendText)
        self.adjustSize()
        # align the legend to the right edge of the envoking button
        self.move(self.envokingButton.pos() - QPoint(self.width() - self.envokingButton.width(), self.height()))
    

class MapView(QGraphicsView):
    """
    A widget that is used as the CentralWidget inside the MainWindow object.

    """
    def __init__(self, parent, world):
        super(MapView, self).__init__()
        self.parent = parent
        #self.mapScene = MapScene(parent, world)
        #self.setScene(self.mapScene)
        self.setScene(MapScene(parent, world))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)
        self.oldHover, self.hover = None, None
        self.oldSelection, self.selection = None, None
        self.rightSelection = None
        self.mapMode = 1
        self._numScheduledScalings = 0
        # Right-click menu
        self.contextMenu =  QMenu()
        self.menuOption = [QAction() for i in range(10)]
        self.menuOption[1].setIcon(parent.graphics.icon[20])
        for i in range(10):
            self.contextMenu.addAction(self.menuOption[i])
            if i < 2: self.contextMenu.addSeparator()
            else:
                self.menuOption[i].triggered.connect(partial(parent.policyWindow.setMode, i - 2))
        button = QPushButton(self)
        button.setText("Legend")
        button.move(850, self.height() - 40)
        button.setCheckable(True)
        button.released.connect(self.hideOrShowLegend)
        button.setFixedWidth(80)
        self.legendWidget = LegendLabel(self, button, "", [], [])
        self.setStrings()

    def setStrings(self):
        self.menuOption[1].setText(Local.strings[Local.MAIN_PANEL][12])
        for i,j in zip(range(8), (5,4,0,1,2,3,6,7)):
            self.menuOption[i + 2].setText(Local.strings[Local.MAIN_PANEL][i+16])
            self.menuOption[i + 2].setIcon(self.parent.graphics.icon[j+9])
    
    def hideOrShowLegend(self):
        self.legendWidget.setVisible(not self.legendWidget.isVisible())

    def mousePressEvent(self, event):
        if event.button() == Qt.MidButton:
            self.__prevMousePos = event.pos()
    
    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        # Left button - select the country (or deselect if hovered item is not a QGraphicsPolygonItem)
        if event.button() == Qt.LeftButton:
            self.oldSelection = self.selection
            self.selection = item.parent if isinstance(item, QGraphicsPolygonItem) else None
            # refresh the map
            if 8 <= self.mapMode <= 21:
                if self.selection and not (self.selection.id > 1
                    and self.mapMode in (M_DESTAB, M_TREATY, M_PRESS, M_ECONAID)):
                    self.scene().mapPainter.doMapRedraw(self.selection, self.mapMode)
                else:
                    self.selection = self.oldSelection
                    return
            if self.selection != self.oldSelection:
                self.selectNothingEffect()
                if self.selection:
                    if item.id < 2: self.selectSuperpowerEffect()
                    else: self.selectCountryEffect()
                    for i in self.parent.controlPanel.mapModeAction[17:22]: i.setEnabled(True)
                    self.updateMap(item.id)
                else: self.updateMap(None)
            super(MapView, self).mousePressEvent(event)
        # Right button - show up pop-up menu over hovered country
        elif event.button() == Qt.RightButton:
            if isinstance(item, QGraphicsPolygonItem):
                self.rightSelection = self.parent.world.country[item.id]
                availableActions = AVL_ACTIONS[self.parent.world.level - 1]
                for i in range(8):
                    self.menuOption[i+2].setEnabled(self.rightSelection.id > 2 and i in availableActions )
                self.menuOption[0].setText(Local.strings[Local.DATA_COUNTRIES + self.rightSelection.id][Local.CTRY_NAME])
                self.menuOption[0].setIcon(QIcon(self.parent.graphics.flag[self.rightSelection.id]))
                self.contextMenu.exec(QCursor.pos())

    def mouseDoubleClickEvent(self, event):
        """
        Display country close-up on left mouse button dobule click.

        """
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, QGraphicsPolygonItem):
                self.selection = item.parent
                self.parent.closeUpWindow.loadCountry(self.parent.world.country[item.id])

    def setMapMode(self, value):
        self.mapMode = value
        self.scene().mapPainter.doMapRedraw(self.selection, self.mapMode)
        self.parent.controlPanel.updateSelection()

    def selectNothingEffect(self):
        for i in self.parent.controlPanel.mapModeButton[8:17]:
            i.setEnabled(False)
            i.actionOwner.setEnabled(False)
        for i in self.parent.controlPanel.mapModeAction[17:22]: i.setEnabled(False)
        self.parent.controlPanel.updateSelection()
    
    def selectCountryEffect(self):
        for i in self.parent.controlPanel.mapModeButton[8:13]:
            i.setEnabled(True)
            i.actionOwner.setEnabled(True)
        self.parent.controlPanel.updateSelection()

    def selectSuperpowerEffect(self):
        for i,j in zip(self.parent.controlPanel.mapModeButton[8:17], range(8,17,1)):
            if j in INAVL_MAP_MODES[self.parent.world.level - 1]: continue
            i.setEnabled(True)
            i.actionOwner.setEnabled(True)
        self.parent.controlPanel.updateSelection()

    def resetMapView(self):
        self.parent.controlPanel.mapModeAction[1].setChecked(True)
        self.selection = None
        self.selectNothingEffect()
        self.scene().mapPainter.mapMode = 1
        self.updateMap(None)
        self.scene().mapPainter.createLegend(None)

    def updateMap(self, selected):
        self.scene().mapPainter.paint(self.scene().mapPainter.mapMode, selected) 

    def mouseMoveEvent(self, event):
        # Use the middle button for dragging the map
        if event.buttons() == Qt.MidButton:
            offset = self.__prevMousePos - event.pos()
            self.__prevMousePos = event.pos()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + offset.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + offset.x())
        # Highlight country border if mouse moves over the territory
        else:
            self.oldHover = self.hover
            item = self.itemAt(event.pos())
            if isinstance(item, QGraphicsPolygonItem):
                self.hover = item.parent
            else: self.hover = None
            if self.oldHover != self.hover:
                if self.oldHover != None: self.oldHover.setHover(False)
                if self.hover != None: self.hover.setHover(True)

    def wheelEvent(self, event):
        # Check if zooming is enabled
        if not self.parent.menu.options[1].isChecked(): return
        # Zooming event on mouse scroll
        numDegrees = event.angleDelta() / 8
        numSteps = (numDegrees / 15).y()
        self._numScheduledScalings += numSteps
        if self._numScheduledScalings * numSteps < 0:
            self._numScheduledScalings = numSteps
        anim = QTimeLine(350, self)
        anim.setUpdateInterval(20)
        anim.valueChanged.connect(self.scalingTime)
        anim.finished.connect(self.animFinished)
        anim.start()

    def scalingTime(self, x):
        factor = 1.0 + self._numScheduledScalings / 300.0
        self.scale(factor, factor)
    
    def animFinished(self):
        if self._numScheduledScalings > 0: self._numScheduledScalings -= 1
        else:
            self._numScheduledScalings += 1
