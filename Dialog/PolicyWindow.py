from PyQt5.QtWidgets import (QGridLayout, QBoxLayout, QHBoxLayout, QMainWindow,
							QLabel, QRadioButton, QPushButton, QGroupBox, QDialog)
from constants import *
import Local
from GameLogic.Globals import *

class PolicyWindow(QDialog):

    def __init__(self, parent):
        super(PolicyWindow, self).__init__(parent)
        self.parent = parent
        mainLayout = QBoxLayout(QBoxLayout.TopToBottom)
        topLayout = QBoxLayout(QBoxLayout.TopToBottom)
        buttonLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.policy = QGroupBox()
        self.remain = QLabel()
        self.opt = [QRadioButton("Radio " + str(i)) for i in range(6)]
        for i in self.opt: topLayout.addWidget(i)
        self.policy.setLayout(topLayout)

        self.cancel = QPushButton("Cancel")
        self.accept = QPushButton("OK")
        buttonLayout.addWidget(self.cancel)
        buttonLayout.addWidget(self.accept)
        self.cancel.released.connect(self.close)
        self.accept.released.connect(self.doEnactPolicy)
        mainLayout.addWidget(self.policy)
        mainLayout.addWidget(self.remain)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        self.setFixedSize(300,250)
        self.setModal(True)

    def setMode(self, action):
        world = self.parent.world
        actor = world.country[world.human]
        self.target = self.parent.mapView.rightSelection
        self.action = action
        maxVal, avlResrc, mode = 5, 0, 0
        x = actor.diplOpinion[self.target.id]
        for i in self.opt: i.setEnabled(True)
        if action == DESTAB: oldCtrl, mode = actor.destab[self.target.id], 3
        elif action == ECONAID:
            oldCtrl, maxVal = actor.econAid[self.target.id], econAidMax(x)
            _sum = sum([econConv(i) for i in actor.econAid])
            x, avlResrc = 5, (actor.GNP // 44) - (2 * _sum)
            for i in range(4,0,-1):
                if econConv(i + 1) > ((avlResrc // 2) + econConv(oldCtrl)): x = i
            if x < maxVal: maxVal = x
            mode = 2
        elif action == GOVTAID:
            oldCtrl, maxVal, mode = actor.govtAid[self.target.id], milMax(x), 0
            x, avlResrc = 5, actor.getAvailableAid()
            for i in range(4,0,-1):
                if mAidConv(i + 1) * 2 > avlResrc: x = i
            if x < maxVal: maxVal = x
        elif action == INSGAID:
            oldCtrl, mode = actor.insgAid[self.target.id], 0
            x = getMaxLevel((512,128,32,8,1), self.target.strengthRatio, lt=True)
            maxVal = x
            x = insgAidMax(world, actor, self.target)
            if x < maxVal: maxVal = x
            avlResrc = actor.getAvailableAid()
            for i in range(4,0,-1):
                if mAidConv(i + 1) * 2 > avlResrc: x = i
            if x < maxVal: maxVal = x
        elif action == GOVTINTV:
            oldCtrl, x, mode = actor.govtIntv[self.target.id], 5, 1
            maxVal = intvGovtMax(world.level, actor.treaty[self.target.id], x)
            avlResrc = actor.getAvailableMen()
            for i in range(4,0,-1):
                if intvConv(i + 1) > avlResrc: x = i
            if x < maxVal: maxVal = x
        elif action == INGSINTV:
            oldCtrl, maxVal, mode = actor.insgIntv[self.target.id], intvInsgMax(world, actor, self.target), 1
            avlResrc = actor.getAvailableMen()
            for i in range(4,0,-1):
                if intvConv(i + 1) > avlResrc: x = i
        elif action == PRESSURE:
            oldCtrl, mode = actor.pressure[self.target.id], 4
        elif action == TREATY:
            oldCtrl, mode = actor.treaty[self.target.id], 5
            maxVal = treatyMax(world.level, actor.integrity + x - actor.pugnacity)
            if maxVal <= actor.treaty[self.target.id]: maxVal = actor.treaty[self.target.id]
            if actor.treaty[self.target.id] > 0:
                for i in range(actor.treaty[self.target.id]):
                    self.opt[i].setEnabled(False)
        if maxVal < 5:
            for i in range(maxVal + 1, 6, 1): self.opt[i].setEnabled(False)
        self.opt[oldCtrl].setChecked(True)
        # Set strings
        if 1 <= action <= 5:
            self.remain.setText(Local.strings[Local.WINDOW_POLICY][0] + Local.formatValue(avlResrc, action))
        else: self.remain.setText("")
        self.setWindowTitle(Local.strings[Local.DATA_COUNTRIES + self.target.id][Local.CTRY_NAME] + \
            " - " + Local.strings[Local.LABEL_POLICY][action])
        for i in range(6): self.opt[i].setText(Local.parseValue(mode, i))
        self.setVisible(True)

    def doEnactPolicy(self):
        x, human = 0, self.parent.world.country[self.parent.world.human]
        for i in range(6):
            if self.opt[i].isChecked():
                x = i
                break
        doPolicy(self.parent.world, human, self.target, self.action, x)
        self.setVisible(False)