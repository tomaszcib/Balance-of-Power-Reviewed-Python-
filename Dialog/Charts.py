from PyQt5.QtCore import Qt, QMargins, QPointF
from PyQt5.QtGui import QColor, QBrush, QFont, QPen
from PyQt5.QtChart import (QChart, QBarCategoryAxis, QValueAxis, QBarSeries, QBarSet, QLineSeries,
                            QPercentBarSeries)

class HistoryChart(QChart):
    """
    Base class for the charts used within the program.

    """

    BAR_CHART = 0
    PERCENT_CHART = 1

    def __init__(self):
        super(HistoryChart, self).__init__()
        self.pen = QColor(Qt.black)
        self.categories = ["'"+str(i) for i in range(82, 90)]
        font = QFont()
        font.setPixelSize(10)
        self.axisX = QBarCategoryAxis()
        self.axisX.setLabelsFont(font)
        self.axisX.append(self.categories)
        self.addAxis(self.axisX, Qt.AlignBottom)
        self.legend().setVisible(False)
        self.layout().setContentsMargins(0,0,0,0)
        self.setMargins(QMargins(5,5,5,5))
        self.setBackgroundRoundness(0)


class BarChart(HistoryChart):
    """
    Chart used for displaying 4-series bar plots in the History tab in the Close-Up window
    or stacked percent plots in the Economy tab in that window.

    """
    def __init__(self, data, type):
        super(BarChart, self).__init__()
        if type == self.BAR_CHART:
            self.brushes = (QColor(Qt.blue), QColor(Qt.red),
                QBrush(Qt.blue, Qt.Dense5Pattern), QBrush(Qt.red, Qt.Dense5Pattern))
            self.series = QBarSeries()
            axisY = QValueAxis()
            axisY.setRange(0,5)
            axisY.setTickCount(6)
            axisY.setLabelFormat(" ")
            self.addAxis(axisY, Qt.AlignLeft)
        elif type == self.PERCENT_CHART:
            self.brushes = (QColor(Qt.yellow), QColor(255,127,0), QColor(Qt.red))
            self.series = QPercentBarSeries()
        self.setData(data)
        self.addSeries(self.series)
        self.series.attachAxis(self.axisX)
        if type == self.BAR_CHART: self.series.attachAxis(axisY)
        
    def setData(self, data):
        self.series.clear()
        for i,j in zip(data, self.brushes):
            barset = QBarSet("test")
            barset.append(i)
            barset.setBrush(j)
            barset.setPen(self.pen)
            self.series.append(barset)
    
class LineChart(HistoryChart):
    """
    Chart used for displaying either single or double line plots.
    In the first case the color of the line defaults to green,
    for double charts - blue and red are used. 

    """
    def __init__(self, data):
        super(LineChart, self).__init__()
        self.brushes = (QPen(QColor(Qt.blue), 2), QPen(QColor(Qt.red), 2))
        self.singleBrush = QPen(QColor(0,127,0), 2)
        self.series = [QLineSeries() for i in range(len(data))]
        self.setData(data)
        for s in self.series:
            self.addSeries(s)
            s.setPointsVisible(True)
            s.attachAxis(self.axisX)
    
    def setData(self, data):
        for s, d in zip(self.series, data):
            s.clear()
            s.append([QPointF(i,y) for i,y in zip(range(8), d)])
        if len(self.series) == 1: self.series[0].setPen(self.singleBrush)
        else:
            for s,b in zip(self.series, self.brushes):
                s.setPen(b)

    def setAxisRange(self, min, max):
        axisY = QValueAxis()
        axisY.setRange(min, max)
        axisY.setLabelFormat(" ")
        self.addAxis(axisY, Qt.AlignLeft)
        for s in self.series:
            s.attachAxis(axisY)