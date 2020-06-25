from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QGridLayout, QBoxLayout, QHBoxLayout, QMainWindow,
							QLabel, QRadioButton, QPushButton, QGroupBox, QDialog, QTableView,
                            QHeaderView, QTableWidget, QButtonGroup, QTableWidgetItem,
                            QAbstractItemView, QComboBox, QRadioButton)
import Local
from functools import partial
from GameLogic.CrisisHandler import getAdvisorOpinion, doCHumanLoose, doCHumanTough

class NewsWindow(QDialog):

    def __init__(self, parent):
        super(NewsWindow, self).__init__(parent)
        self.parent = parent
        # top table - news list and filters
        self.table = QTableWidget(0,5)
        horizLabels = ["", "", "", "", ""]
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.itemSelectionChanged.connect(self.doDisplayNewsHeadline)
        self.table.setHorizontalHeaderLabels(horizLabels)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setWordWrap(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        topLayout = QGridLayout()
        topLayout.addWidget(self.table, 0,1)
        filterLayout = QBoxLayout(QBoxLayout.TopToBottom)
        self.filters = [QPushButton(parent.graphics.icon[23 + i], "") for i in range(5)]
        filterGroup = QButtonGroup()
        for i,j in zip(self.filters, range(5)):
            i.setFixedSize(120,32)
            i.setAutoExclusive(True)
            i.setCheckable(True)
            i.released.connect(partial(self.doRefreshNews, j))
            filterGroup.addButton(i)
            filterLayout.addWidget(i)
            filterLayout.addSpacing(-5)
        filterLayout.addSpacing(30)
        filterLayout.setAlignment(Qt.AlignVCenter)
        self.ctryList = QComboBox()
        self.ctryList.setMaxVisibleItems(10)
        self.ctryList.addItems([Local.strings[Local.DATA_COUNTRIES + i][Local.CTRY_NAME] for i in range(80)])
        self.ctryList.currentIndexChanged.connect(partial(self.doRefreshNews, 5))
        self.localNews = QRadioButton()
        self.localNews.released.connect(partial(self.doRefreshNews, 5))
        filterGroup.addButton(self.localNews)
        filterLayout.addWidget(self.localNews)
        filterLayout.addWidget(self.ctryList)
        topLayout.addLayout(filterLayout,0,0)
        topLayout.setContentsMargins(-50,0,0,0)
        self.table.setFixedHeight(220)


        # left half - news
        buttons = QBoxLayout(QBoxLayout.LeftToRight)
        leftLayout = QBoxLayout(QBoxLayout.TopToBottom)
        leftLayout.setContentsMargins(-80,0,0,0)
        self.newsHline = QLabel()
        self.newsHline.setWordWrap(True)
        self.newsHline.setFixedHeight(40)
        leftLayout.addSpacing(25)
        leftLayout.addWidget(self.newsHline)
        leftLayout.addSpacing(30)
        self.question = QPushButton()
        self.backDown = QPushButton()
        self.question.released.connect(self.doTough)
        self.backDown.released.connect(self.doLoose)
        for i in (self.question, self.backDown): buttons.addWidget(i)
        leftLayout.addLayout(buttons)
        self.reactionLine = QLabel()
        self.reactionLine.setFixedHeight(30)
        self.reactionLine.setWordWrap(True)
        leftLayout.addSpacing(20)
        leftLayout.addWidget(self.reactionLine)
        leftLayout.addSpacing(20)
        leftInfoLayout = [QBoxLayout(QBoxLayout.LeftToRight) for i in range(3)]
        self.leftInfo = [QLabel() for i in range(3)]
        self.leftInfoVal = [QLabel()  for i in range(3)]
        for i in range(3):
            leftInfoLayout[i].addWidget(self.leftInfo[i])
            leftInfoLayout[i].addWidget(self.leftInfoVal[i])
            leftLayout.addLayout(leftInfoLayout[i])
            if i < 2: leftLayout.addSpacing(-5)
        
        # right half - advisory
        rightLayout = QBoxLayout(QBoxLayout.TopToBottom)
        rightLayout.setContentsMargins(0,-50,0,0)
        #rightLayout.addWidget(self.advisory)
        headsLayout = QBoxLayout(QBoxLayout.LeftToRight)
        headsColumn = [QBoxLayout(QBoxLayout.TopToBottom) for i in range(2)]
        head = [QBoxLayout(QBoxLayout.LeftToRight) for i in range(4)]
        self.picture = [QLabel() for i in range(4)]
        self.advice = [QLabel() for i in range(4)]
        for i in range(4):
            self.picture[i].setPixmap(parent.graphics.advisor[i])
            self.advice[i].setWordWrap(True)
            self.advice[i].setFixedWidth(100)
            head[i].addWidget(self.picture[i])
            head[i].addWidget(self.advice[i])
            headsColumn[i//2].addLayout(head[i])
        self.closeUpButton = QPushButton()
        
        for i in range(2): headsLayout.addLayout(headsColumn[i])
        rightLayout.addLayout(headsLayout)

        # save right and left layouts into groups
        self.detailGroup = [QGroupBox() for i in range(3)]
        self.detailGroup[0].setLayout(leftLayout)
        self.detailGroup[1].setLayout(rightLayout)
        self.detailGroup[2].setLayout(topLayout)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.detailGroup[2], 0, 0, 1, 2)
        for i in range(2): mainLayout.addWidget(self.detailGroup[i], 1, i)
        
        self.setStrings()
        self.setLayout(mainLayout)
        self.setFixedSize(830, 590)
        self.setModal(True)
        self.beingQuestioned = False

    def filterCondition(self, n, mode):
        if mode == 0: return n.actor == self.parent.world.USA and n.new > n.old     #USA Actions
        elif mode == 1: return n.actor == self.parent.world.USA and n.new < n.old   #USA Other
        elif mode == 2: return n.actor == self.parent.world.USSR and n.new > n.old  #USSR Actions
        elif mode == 3: return n.actor == self.parent.world.USSR and n.new < n.old  #USSR Other
        elif mode == 4: return n.actor.id  >= 2                                     #Minor actions
        elif mode == 6: return n.isQuestioned                                       #AI turn - questions our moves
        else:                                                                       #Filter by country
            return self.sortedCountries[self.ctryList.currentIndex()] in (n.actor.id, n.target.id)

    def doRefreshNews(self, mode):
        """
        Populate the table with event headlines filtered in accordance to the given 'mode'

        """
        self.mode = mode
        if mode == 5: self.localNews.setChecked(True)
        news = self.parent.world.news
        self.table.setRowCount(0)
        # Filter the news and store successfully filtered objects in the self.news property
        self.news = []
        for n in news:
            if self.filterCondition(n, mode): self.news.append(n)
        for i,n in zip(range(len(self.news)), self.news):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(
                QIcon(self.parent.graphics.flag[n.actor.id]), Local.strings[Local.DATA_COUNTRIES + n.actor.id][Local.CTRY_NAME]))
            self.table.setItem(i, 1, QTableWidgetItem(
                QIcon(self.parent.graphics.flag[n.target.id]), Local.strings[Local.DATA_COUNTRIES + n.target.id][Local.CTRY_NAME]))
            self.table.setItem(i, 2, QTableWidgetItem(n.getTypeName()))
            if n.action not in (0,6): prefix = "\u25bc" if n.new < n.old else "\u25b2"
            else: prefix = ""
            self.table.setItem(i, 3, QTableWidgetItem(prefix + n.getActionValue(False)))
            checkedItem = QTableWidgetItem()
            checkedItem.setText("" if n.crisisVal else "✔")
            checkedItem.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, checkedItem)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setDefaultSectionSize(35)

    def showUp(self):
        mode = self._getCurrentMode()
        self.doRefreshNews(mode)
        self.setVisible(True)

    def doDisplayNewsHeadline(self):
        rowNum = self.table.currentRow()
        if rowNum < 0:
            self.hideAdvisors()
            self.newsHline.setText("")
            self.closeUpButton.setEnabled(False)
            return
        headline = self.news[rowNum]
        self.newsHline.setText(headline.text)
        # Questionable policy - display advisory panel
        if not headline.crisisVal:
            self.question.setEnabled(True)
            self.backDown.setEnabled(False)
            for i in range(4):
                self.advice[i].setText(getAdvisorOpinion(self.parent.world, headline, i + 1))
                self.picture[i].setVisible(True)
        else: self.hideAdvisors()

    def doLoose(self):
        """Action performed by releasing the 'back down' button"""
        doCHumanLoose(self, self.parent.world, self.news[self.table.currentRow()])
    
    def doTough(self):
        """Action performed by releasing the 'question' button"""
        doCHumanTough(self, self.parent.world, self.news[self.table.currentRow()])


    def hideAdvisors(self):
        self.backDown.setEnabled(False)
        self.question.setEnabled(False)
        for i in range(4):
            self.picture[i].setVisible(False)
            self.advice[i].setText("")
        self.setRiskValuesVisible(False)

    def setRiskValuesVisible(self, visible):
        for i,j,k in zip(self.leftInfo, self.leftInfoVal, range(3)):
            i.setText(Local.strings[Local.CRISIS_FILTER][22+k] if visible else "")
            j.setText("")

    def setLocked(self, value):
        if not value:
            previousRow = self.table.currentRow()
            self.backDown.setText(Local.strings[Local.CRISIS_BD_BUTTON][0])
            self.reactionLine.setText("")
            self.question.setDisabled(value)
            self.question.setText(Local.strings[Local.CRISIS_SUPER_BUTTON][9])
            self.doRefreshNews(self._getCurrentMode())
            self.table.selectRow(previousRow)
        self.setRiskValuesVisible(value)
        self.table.setDisabled(value)
        for i in self.filters: i.setDisabled(value)
        self.ctryList.setDisabled(value)
        self.localNews.setDisabled(value)

    def _getCurrentMode(self):
        if self.beingQuestioned: return 6
        if self.localNews.isChecked(): return 5
        for i,j in zip(range(5), self.filters):
            if j.isChecked():
                return i

    def endOfCrisis(self):
        self.setLocked(False)


    def setTableLocked(self, value):
        for i in self.filters: i.setEnabled(value)
        self.table.setEnabled(value)

    def setStrings(self):
        self.table.setHorizontalHeaderLabels(Local.strings[Local.CRISIS_FILTER][8:13])
        for i in range(5):
            if i < 3:
                self.detailGroup[i].setTitle(Local.strings[Local.CRISIS_FILTER][i + 25])
            self.filters[i].setText(Local.strings[Local.CRISIS_FILTER][i])
        while self.ctryList.count() > 0: self.ctryList.removeItem(0)
        ctryNames = [Local.strings[Local.DATA_COUNTRIES + i ][Local.CTRY_NAME] for i in range(len(self.parent.world.country))]
        self.sortedCountries = sorted(range(len(ctryNames)), key=ctryNames.__getitem__)
        self.ctryList.addItems([ctryNames[self.sortedCountries[i]] for i in range(len(ctryNames))])
        for i in range(len(ctryNames)):
            self.ctryList.setItemIcon(i, QIcon(self.parent.graphics.flag[self.sortedCountries[i]]))
        
        self.localNews.setText(Local.strings[Local.CRISIS_FILTER][5])
        self.question.setText(Local.strings[Local.CRISIS_SUPER_BUTTON][9])
        self.backDown.setText(Local.strings[Local.CRISIS_BD_BUTTON][0])
        self.reactionLine.setText("")
        self.newsHline.setText("")