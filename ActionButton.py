from PyQt5.QtWidgets import QPushButton

class ActionButton(QPushButton):
    """
    Button that is commected to a QAction. Used for the map mode buttons
    in the ControlPanel class.

    """

    actionOwner = None

    def setAction(self, action):
        self.actionOwner = action
        self.updateButtonStatusFromAction()
        action.changed.connect(self.updateButtonStatusFromAction)
        self.clicked.connect(self.actionOwner.trigger)

    def updateButtonStatusFromAction(self):
        if not self.actionOwner: return
        self.setToolTip(self.actionOwner.text())
        self.setIcon(self.actionOwner.icon())
        self.setEnabled(self.actionOwner.isEnabled())
        self.setCheckable(self.actionOwner.isCheckable())
        self.setChecked(self.actionOwner.isChecked())