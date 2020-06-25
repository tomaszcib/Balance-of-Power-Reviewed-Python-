from PyQt5.QtWidgets import (QMenu, QMenuBar, QAction, QActionGroup)
from os import listdir
from os.path import isfile, join
from functools import partial
import Local

class Menu(QMenuBar):

    LANG_PATH = "./data/local"

    def __init__(self, parent):
        super(Menu, self).__init__()
        self.submenu = [QMenu() for i in range(4)]
        self.mapModeSubmenu = [QMenu() for i in range(5)]
        self.mapResrcSubmenu = [QMenu() for i in range(4)]
        self.fileMenuAction = [QAction() for i in range(5)]
        self.helpMenuAction = [QAction() for i in range(2)]
        self.options = [QAction() for i in range(4)]
        self.languageMenu = QMenu()

        # File menu options
        for i in range(5):
            if i in (3,4): self.submenu[0].addSeparator()
            self.submenu[0].addAction(self.fileMenuAction[i])
        self.fileMenuAction[0].triggered.connect(partial(parent.newGameWindow.setVisible, True))

        # Help menu options
        for i in self.helpMenuAction: self.submenu[3].addAction(i)

        # Map mode submenus
        for i in self.mapResrcSubmenu:
            self.mapModeSubmenu[3].addMenu(i)
        for i,j in zip(parent.controlPanel.mapModeAction, range(len(parent.controlPanel.mapModeAction))):
            if j in range(22,33,1):
                j -= 22
                self.mapResrcSubmenu[0 if j < 2 else (j+1)//3].addAction(i)
            else:
                if j < 8: toInsert = 0
                elif 8 <= j <= 16: toInsert = 1
                elif 17 <= j <= 21: toInsert = 2
                elif 33 <= j <= 34: toInsert = 3
                else: toInsert = 4
                self.mapModeSubmenu[toInsert].addAction(i)
        for i in self.mapModeSubmenu: self.submenu[1].addMenu(i)
        
        # Options menu
        self.submenu[2].addAction(self.options[0])
        self.options[0].setCheckable(True)
        self.submenu[2].addSeparator()
        #for i in self.options[1:4]: self.submenu[2].addAction(i)
        for i in range(1,4,1):
            self.submenu[2].addAction(self.options[i])
            self.options[i].setCheckable(i < 3)
        self.submenu[2].addSeparator()
        self.submenu[2].addMenu(self.languageMenu)

        # Add all menus to the bar
        for i in self.submenu: self.addMenu(i)
        
        self.loadLanguages()
        self.setStrings()

    def setStrings(self):
        strs = Local.strings[Local.MENU]
        for i in range(4): self.submenu[i].setTitle(strs[i + 54])
        for i in range(4): self.mapResrcSubmenu[i].setTitle(strs[i + 22])
        for i in range(5): self.mapModeSubmenu[i].setTitle(strs[i + 26])
        for i in range(5): self.fileMenuAction[i].setText(strs[i + 58])
        for i in range(2): self.helpMenuAction[i].setText(strs[i + 63])
        for i in range(4): self.options[i].setText(strs[i + 65])
        self.languageMenu.setTitle(strs[69])

    def loadLanguages(self):
        self.languages = dict.fromkeys([f for f in listdir(self.LANG_PATH) if isfile(join(self.LANG_PATH, f))])
        for lang in self.languages:
            self.languages[lang] = QAction(lang.split(".")[0].capitalize())
        languageGroup = QActionGroup(self)
        for lang in self.languages.keys():
            i = self.languages[lang]
            i.setCheckable(True)
            languageGroup.addAction(i)
            self.languageMenu.addAction(i)

