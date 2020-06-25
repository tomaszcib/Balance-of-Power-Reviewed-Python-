from PyQt5.QtCore import QBuffer, QIODevice
from PyQt5.QtGui import (QPixmap, QIcon, QColor)

class Graphics:
    """
    Loads the in-game graphics into the program memory. An object of this class
    is declared in the MainWindow main object.

    """
    def __init__(self):
        #Program icon
        self.progIcon = QPixmap("img/icon175x175.png")
        #Flags
        _img = QPixmap("img/flags.png")
        self.flag = [QPixmap(_img.copy(37 * (i % 10), 22 * (i // 10), 36, 22)) for i in range(80)]
        #buffer the flags - used for showing them in system tooltips
        buffer = [QBuffer() for i in range(80)]
        for img,buf in zip(self.flag, buffer):
            buf.open(QIODevice.WriteOnly)
            img.scaledToHeight(12).save(buf, "PNG", quality=100)
        self.flagToolTip = [bytes(i.data().toBase64()).decode() for i in buffer]
        self.emptyFlag = QPixmap(36,22)
        self.emptyFlag.fill(QColor(255,255,255,255))

        # Action icons
        _img = QPixmap("img/icons.png")
        self.icon = [QIcon(_img.copy(65 * (i % 10), 65 * (i // 10), 64, 64)) for i in range(30)]

        # Advisors
        self.advisor = [QPixmap("img/adv" + str(i + 1) + ".png") for i in range(4)]

