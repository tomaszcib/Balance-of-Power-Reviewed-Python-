from PyQt5.QtCore import Qt, QMargins, QPoint
from PyQt5.QtGui import QColor, QBrush, QFont, QPainter, QPixmap
from PyQt5.QtWidgets import (QGridLayout, QBoxLayout, QHBoxLayout, QGroupBox, QScrollArea, QTextEdit,
							QLabel, QPushButton, QWidget, QDialog, QTabWidget, QGraphicsView)
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from Dialog.Charts import *
from GameLogic.Globals import intvConv, mAidConv, econConv
from random import randint
from constants import *
import Local

class BasicInfoTab(QWidget):

    def __init__(self, parent):
        super(BasicInfoTab, self).__init__()
        mainLayout = QBoxLayout(QBoxLayout.TopToBottom)
        mainTableLayout = QBoxLayout(QBoxLayout.LeftToRight)
        headerLayout = QBoxLayout(QBoxLayout.LeftToRight)
        mainLowerLayout = QBoxLayout(QBoxLayout.LeftToRight)
        column = [QBoxLayout(QBoxLayout.TopToBottom) for i in range(4)]
        lowerColumn = [QBoxLayout(QBoxLayout.TopToBottom) for i in range(2)]
        self.hint = QLabel()
        headerLayout.addSpacing(172)
        headerLayout.addWidget(self.hint)
        self.topHeader = [QLabel(str(i)) for i in range(3)]
        column[0].addSpacing(20)
        for i in range(1,4): column[i].addWidget(self.topHeader[i-1])
        self.paramName = [QLabel("param " + str(i)) for i in range(20)]
        for i in range(20):
            if i <= 11: column[0].addWidget(self.paramName[i])
            else: lowerColumn[0].addWidget(self.paramName[i])
        self.sprpwrVal = [QLabel("data " + str(i)) for i in range(24)]
        for i in range(24):
            column[1 if i < 12 else 2].addWidget(self.sprpwrVal[i])
        self.otherVal = [QLabel() for i in range(12)]
        for i in self.otherVal: column[3].addWidget(i)
        self.infoVal = [QLabel("info " + str(i)) for i in range(8)]
        for i in self.infoVal: lowerColumn[1].addWidget(i)
        # Local news section
        self.localNewsGroup = QGroupBox("Local insights")
        self.localNewsLabel = QTextEdit()
        tmp = QBoxLayout(QBoxLayout.LeftToRight)
        tmp.addWidget(self.localNewsLabel)
        self.localNewsGroup.setLayout(tmp)
        # putting it all together
        for i in column: mainTableLayout.addLayout(i)
        for i in lowerColumn: mainLowerLayout.addLayout(i)
        mainLowerLayout.addSpacing(50)
        mainLowerLayout.addWidget(self.localNewsGroup)
        #preview = QGraphicsView(parent.mapView.scene())
        #preview.setFixedSize(200,200)
        #mainLowerLayout.addWidget(preview)
        mainLayout.addLayout(mainTableLayout)
        mainLayout.addLayout(headerLayout)
        mainLayout.addSpacing(5)
        mainLayout.addLayout(mainLowerLayout)
        self.setLayout(mainLayout)
    
    def loadCountry(self, world, country):
        c = country
        visibleTo = (6,8,12,12)[world.level - 1]
        # USA and USSR - resource usage and availability
        if c.id < 2:
            # Set column names
            for i in range(2): self.topHeader[i].setText("<b>%s</b>" % Local.strings[Local.WINDOW_INFO][i + 23])
            self.topHeader[2].setText("")
            # Used resources
            sumIntvG = sum([intvConv(i) for i in c.govtIntv[2:]])
            sumIntvI = sum([intvConv(i) for i in c.insgIntv[2:]])
            sumAidG = sum([mAidConv(i) for i in c.govtAid[2:]])
            sumAidI = sum([mAidConv(i) for i in c.insgAid[2:]])
            sumEconAid = sum([econConv(i) for i in c.econAid[2:]])
            # Available resources
            for j in range(2, 7, 1):
                if j == 2: y, avlResrc = 2 * sumAidG, c.getAvailableAid()
                elif j == 3: y, avlResrc = 2 * sumAidI, c.getAvailableAid()
                elif j == 4: y, avlResrc = sumIntvG, c.getAvailableMen()
                elif j == 5: y, avlResrc = sumIntvI, c.getAvailableMen()
                elif j == 6:
                    y = 2 * sumEconAid
                    avlResrc = (c.GNP // 44) - y
                self.sprpwrVal[j].setText(Local.formatValue(y, j))
                self.sprpwrVal[j + 12].setText(Local.formatValue(avlResrc, j))
        # Minor countries - superpower policies
        else:
            for i in range(3): self.topHeader[i].setText("<b>%s</b>" % Local.strings[Local.WINDOW_INFO][i + 20])
            for s in world.country[:2]:
                s.setMaxPolicy()
                for m in range(12):
                    toWrite = ""
                    labelType, val, old, maxNum, maxVal = c.getCloseUpInfoValue(world, s, m)
                    # prestige value
                    if m == 1:
                        self.sprpwrVal[s.id * 12 + m].setText(str(val))
                        continue
                    elif 2 <= m <= 9:
                        if old > val: toWrite += "\u25bc "
                        elif old < val: toWrite += "\u25b2 "
                    toWrite += Local.parseValue(labelType, val)
                    if maxVal == val: toWrite = "{" + toWrite + "}"
                    self.sprpwrVal[s.id * 12 + m].setText(toWrite)
            self.otherVal[1].setText(str(c.prestigeVal // 8))
            # Total aid and intervene
            for i in range(2,6,1):
                if i == 2: val = sum([mAidConv(k.govtAid[c.id]) * 2 for k in world.country])
                elif i == 3: val = sum([mAidConv(k.insgAid[c.id]) * 2 for k in world.country])
                elif i == 4: val = sum([intvConv(k.govtIntv[c.id]) for k in world.country])
                elif i == 5: val = sum([intvConv(k.insgIntv[c.id]) for k in world.country])
                self.otherVal[i].setText(Local.formatValue(val, i))
        # Clear out unnecessary data
        visibilitySet = CLOSE_UP_SUPERPWR if c.id < 2 else CLOSE_UP_AVL_DATA
        for i in range(12):
            #visible = i in CLOSE_UP_AVL_DATA[world.level - 1]
            if i not in visibilitySet[world.level - 1]:
                self.paramName[i].setText("")
                self.sprpwrVal[i].setText("")
                self.sprpwrVal[i+12].setText("")
            else: self.paramName[i].setText("<b>%s</b>" % (Local.strings[Local.WINDOW_INFO][i]))
        if c.id < 2:
            for i in range(12): self.otherVal[i].setText("")
        
        # Get basic information for both superpower or minor country
        self.infoVal[0].setText(Local.strings[Local.TAG_INSURGENCY][c.getInsurgency()] \
            + " -- " + Local.strings[Local.TAG_INSG_PACE][c.getInsurgencyChange()])
        self.infoVal[1].setText(Local.strings[Local.TAG_IDEOLOGY][c.getIdeology("govt")])
        self.infoVal[2].setText(Local.strings[Local.TAG_STREMGTH][c.getMilPower()])
        self.infoVal[3].setText(Local.strings[Local.TAG_SPHERE][c.getSphOfInfluence(world)])
        self.infoVal[4].setText(Local.strings[Local.TAG_COUP_CHANCE][c.getGovtStability()] \
            + " -- " + Local.strings[Local.TAG_COUP_PACE][c.getGovtStabilityChange()])
        self.infoVal[5].setText(Local.strings[Local.DATA_COUNTRIES + c.id][Local.CTRY_CAPITAL])
        self.infoVal[6].setText(Local.strings[Local.DATA_COUNTRIES + c.id][Local.CTRY_LEADER_TITLE] + " " + c.leaderName)
        self.infoVal[7].setText(c.getInsurgentsName())

        # Load local news
        self.localNewsLabel.setText(c.localNews)
        

    def setStrings(self):
        for i in range(20):
            self.paramName[i].setText("<b>%s</b>" % (Local.strings[Local.WINDOW_INFO][i]))
        self.hint.setText(Local.strings[Local.WINDOW_INFO][25])


class HistoryTab(QWidget):

    def __init__(self, parent):
        super(HistoryTab, self).__init__()
        columnLayout = QBoxLayout(QBoxLayout.LeftToRight)
        mainLayout = QBoxLayout(QBoxLayout.TopToBottom)
        legend = QLabel()
        chartViews = [QChartView() for i in range(9)]
        self.charts = [LineChart([_random(10,100,8)]), LineChart([_random(10,100,8)]), LineChart([_random(10,100,8) for i in range(2)])] + \
            [BarChart([_random(0,5,8) for i in range(4)], 0) for k in range(4)] + [LineChart([_random(10,100,8) for i in range(2)]),LineChart([_random(10,100,8)])] 
        _setCharts(self.charts, chartViews)
        # Set ranges for line charts
        self.charts[0].setAxisRange(0,80)   # Insurgency
        self.charts[1].setAxisRange(0,20)   # govt stability
        self.charts[2].setAxisRange(0,128)  # finl. prob.
        self.charts[7].setAxisRange(-127,127) # dipl. opinion
        self.charts[8].setAxisRange(0,336)  # milit. pressure
        gridLayout = QGridLayout()
        for i,chart in zip(range(9), chartViews):
            gridLayout.addWidget(chart, i // 3, i % 3)
        self.setLayout(gridLayout)
        #mainLayout.addWidget

    def loadCountry(self, level, cHistory):
        self.charts[0].setData(cHistory.sqrtStrength)
        self.charts[3].setData(cHistory.govtAid + cHistory.insgAid)
        self.charts[6].setData(cHistory.govtIntv + cHistory.insgIntv)
        self.charts[7].setData(cHistory.diplOpinion)
        self.charts[8].setData(cHistory.milPressure)
        if level > 1:
            self.charts[1].setData(cHistory.govtPopul)
            self.charts[4].setData(cHistory.econAid + cHistory.destab)
        if level > 2:
            self.charts[2].setData(cHistory.finlProb)
            self.charts[5].setData(cHistory.treaty + cHistory.pressure)
    
    def setStrings(self):
        for i in range(9):
            self.charts[i].setTitle(Local.strings[Local.WINDOW_HISTORY][i])

class EconomyTab(QWidget):

    def __init__(self, parent):
        super(EconomyTab, self).__init__()
        mainLayout = QBoxLayout(QBoxLayout.TopToBottom)
        rowLayout = [QBoxLayout(QBoxLayout.LeftToRight) for i in range(2)]
        grandTableLayout = QBoxLayout(QBoxLayout.LeftToRight)
        chartLayout = [QBoxLayout(QBoxLayout.TopToBottom) for i in range(5)]
        self.title = [QLabel("Title " + str(i)) for i in range(5)]
        for i in range(5): chartLayout[i].addWidget(self.title[i])
        chartLayout[0].addLayout(grandTableLayout)
        rowLayout[0].addLayout(chartLayout[0])
        rowLayout[0].addLayout(chartLayout[1])
        for i in range(2,5,1):
            rowLayout[1].addLayout(chartLayout[i])
        mainLayout.addLayout(rowLayout[0])
        mainLayout.addSpacing(50)
        mainLayout.addLayout(rowLayout[1])
        dataColLayout = [QBoxLayout(QBoxLayout.TopToBottom) for i in range(6)]
        for i in range(5):
            grandTableLayout.addLayout(dataColLayout[i])
        self.gnpCol = [QLabel("Text " + str(i)) for i in range(20)]
        for i in range(20): dataColLayout[i//5].addWidget(self.gnpCol[i])
        tableLayout = [QBoxLayout(QBoxLayout.LeftToRight) for i in range(3)]
        for i in range(3): chartLayout[i + 2].addLayout(tableLayout[i])
        self.charts = [BarChart([[randint(10,100) for i in range(8)] for j in range(3)], 1)] + \
            [LineChart([[randint(10,100) for i in range(8)] for j in range(1)]) for k in range(3)]
        chartViews = [QChartView() for i in range(4)]
        chartViews[0].setFixedSize(250,170)
        _setCharts(self.charts, chartViews)
        for i in range(4): chartLayout[i+1].addWidget(chartViews[i])
        lowChartsColumnLayout = [QBoxLayout(QBoxLayout.TopToBottom) for i in range(6)]
        for i in range(6): tableLayout[i//2].addLayout(lowChartsColumnLayout[i])
        self.data = [QLabel("Data " + str(i)) for i in range(12)]
        for i in range(12): lowChartsColumnLayout[i//2].addWidget(self.data[i])
        self.setLayout(mainLayout)

    def loadCountry(self, world, country):
        h = country.history
        for i in range(4):
            self.gnpCol[6 + i].setText(Local.formatValue(country.getNominalGNP(i), 11))
            self.gnpCol[11 + i].setText(Local.formatValue(country.getGNPpcap(i), 12))
            if i < 3:
                self.gnpCol[16 + i].setText("{:.2%}".format(country.gnpFrac[i] / 255))
        self.data[3].setText(Local.formatValue(country.population, 10))
        self.data[7].setText(Local.formatValue(country.getNominalGNP(i), 11))
        self.data[11].setText(Local.formatValue(country.getGNPpcap(i), 12))
        self.charts[0].setData(country.history.gnpFrac)

    def setStrings(self):
        self.gnpCol[0].setText("")
        self.gnpCol[-1].setText("")
        legendColors = (QColor(Qt.yellow), QColor(255,127,0), QColor(Qt.red), QColor(0,127,0))
        for i in range(5):
            self.title[i].setText("<b>%s</b>" % Local.strings[Local.WINDOW_ECONOMY][i + 7])
            if i < 4:
                square = QPixmap(75, 15)
                square.fill(QColor("transparent"))
                squarePainter = QPainter(square)
                squarePainter.drawText(QPoint(20,11), Local.strings[Local.WINDOW_ECONOMY][i])
                squarePainter.setBrush(legendColors[i])
                squarePainter.drawRect(4,2,10,10)
                self.gnpCol[i+1].setPixmap(square)
                squarePainter.end()
            if i < 3: self.gnpCol[(i+1)*5].setText("<b>%s</b>" % Local.strings[Local.WINDOW_ECONOMY][i + 4])
        for i in (0,1,4,5,8,9):
            self.data[i].setText("<b>%s</b>" % Local.strings[Local.WINDOW_ECONOMY][12 + i % 2])



def _setCharts(charts, chartViews):
    for i,j in zip(charts, chartViews):
        j.setChart(i)

def _random(a,b,n):
    return [randint(a,b) for i in range(n)]

class CloseUpWindow(QDialog):
    """
    The main Close-Up class. Consists of QTabWidget with three tabs
    - basic info tab, history tab and economy tab.
    All child tab data updates are called from within this object.
    
    """

    def __init__(self, parent):
        super(CloseUpWindow, self).__init__(parent)
        self.parent = parent
        self.basicInfoTab = BasicInfoTab(parent)
        self.historyTab = HistoryTab(parent)
        self.economyTab = EconomyTab(parent)
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.basicInfoTab, "")
        self.tabWidget.addTab(self.historyTab, "")
        self.tabWidget.addTab(self.economyTab, "")
        mainLayout = QBoxLayout(QBoxLayout.TopToBottom)
        mainLayout.addWidget(self.tabWidget)
        self.setLayout(mainLayout)
        self.setFixedSize(800, 600)
        self.setModal(True)
        self.setStrings()

    def loadCountry(self, country):
        self.setWindowTitle(Local.strings[Local.DATA_COUNTRIES + country.id][Local.CTRY_NAME] + " - " + \
            Local.strings[Local.MAIN_PANEL][12])
        self.basicInfoTab.loadCountry(country.parent, country)
        self.historyTab.loadCountry(self.parent.world.level, country.history)
        self.economyTab.loadCountry(country.parent, country)
        self.setVisible(True)

    def setStrings(self):
        self.basicInfoTab.setStrings()
        self.historyTab.setStrings()
        self.economyTab.setStrings()
        self.tabWidget.setTabText(0, Local.strings[Local.WINDOW_INFO][26])
        self.tabWidget.setTabText(1, Local.strings[Local.WINDOW_HISTORY_LEGEND][4])
        self.tabWidget.setTabText(2, Local.strings[Local.WINDOW_ECONOMY][14])