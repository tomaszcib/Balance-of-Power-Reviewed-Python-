from PyQt5.QtCore import Qt, QMargins, QPoint
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import (QGridLayout, QBoxLayout, QLabel, QWidget, QDialog,)
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from Dialog.Charts import *
import Local

class ScoresWindow(QDialog):

    def __init__(self, parent):
        super(ScoresWindow, self).__init__(parent)
        self.parent = parent
        mainLayout = QBoxLayout(QBoxLayout.TopToBottom)
        columnLayout = QBoxLayout(QBoxLayout.LeftToRight)
        column = [QBoxLayout(QBoxLayout.TopToBottom) for i in range(3)]
        for i in column: columnLayout.addLayout(i)
        self.cell = [QLabel() for i in range(9)]
        for i in range(9): column[i//3].addWidget(self.cell[i])
        chartView = QChartView()
        axisY = QValueAxis()
        axisY.setRange(-700,700)
        axisY.setLabelFormat("%d")
        self.chart = LineChart(((10,20,30,40,50,60,70,80),(0,-10,-20,-30,-40,50,-20,0)))
        self.chart.addAxis(axisY, Qt.AlignLeft)
        for i in self.chart.series:
            i.attachAxis(axisY)
        chartView.setChart(self.chart)
        self.level = QLabel()
        mainLayout.addLayout(columnLayout)
        mainLayout.addWidget(chartView)
        self.setLayout(mainLayout)
        self.setFixedSize(300,400)
        self.setModal(True)
        self.setStrings()

    def setStrings(self):
        self.setWindowTitle(Local.strings[Local.WINDOW_SCORES][-1])
        for i,j in zip(range(4), (1,2,3,6)):
            self.cell[j].setText("<b>%s</b>" % Local.strings[Local.WINDOW_SCORES][i])

    def update(self):
        for i,s in zip(range(2), self.parent.world.country[:2]):
            self.cell[4 + i * 3].setText(str(s.score - s.oldScore))
            self.cell[5 + i * 3].setText(str(s.score - s.initScore))
        self.chart.setData((self.parent.world.USA.historyScore, self.parent.world.USSR.historyScore))