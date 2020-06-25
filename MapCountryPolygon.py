from PyQt5.QtGui import QBrush, QColor, QPen
import Local


class MapCountryPolygon:
    """
    Graphic representation of a country. Contains one or more
    QPolygonGraphicsItem objects. Reference to this class object
    are stored within GameLogic.Country objects.

    """

    def __init__(self, parent, id, polygon):
        super(MapCountryPolygon, self).__init__()
        self.parent = parent
        self.id = id
        self.flagStr = '<img src="data:image/png;base64,{}">'.\
                format(self.parent.parent.graphics.flagToolTip[self.id])
        self.value = ""
        self.polys = []
        self.addPolygon(id, polygon)

    def addPolygon(self, id, polygon):
        self.polys.append(self.parent.addPolygon(polygon))
        self.polys[-1].setPen(QColor(0,0,0))
        self.polys[-1].id = id
        self.polys[-1].parent = self
        self.polys[-1].setToolTip(
            '<img src="data:image/png;base64,{}"> - '.format(self.parent.parent.graphics.flagToolTip[id]))

    def setColor(self, color, caption):
        color.setAlpha(220)
        self.value = caption
        for p in self.polys:
            p.setBrush(QBrush(color))
            p.setToolTip(self.flagStr \
                + Local.strings[Local.DATA_COUNTRIES + self.id][Local.CTRY_NAME] \
                + " - " +caption)

    def setHover(self, value):
        pen = QPen(QColor(0,0,0), 3 if value else 1)
        for p in self.polys:
            p.setPen(pen)