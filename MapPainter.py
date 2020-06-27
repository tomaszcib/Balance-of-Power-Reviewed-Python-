from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from constants import *
import Local

class MapPainter:

    def __init__(self, parent, world):
        super(MapPainter, self).__init__()

        self.parent = parent
        self.world = world

        self.recalculateMapBuffer()

        # Prepare color schemes
        # 1 - diplomatic opinion green-white-red
        self.legendDiplo = [QColor(255, i * 63, i * 63) for i in range(4)] + [QColor(Qt.white)]
        self.legendDiplo += [QColor(255 - (i + 1) * 63, 255 - (i + 1) * 32, 255 - (i + 1) * 63) for i in range(4)]

        # 2 - spheres of infl: blue-white-red
        self.legendSphere = [QColor(255, i * 42, i * 42) for i in range(6)] + [QColor(Qt.white)]
        self.legendSphere += [QColor(255 - (i + 1) * 42, 255 - (i + 1) * 42, 255) for i in range(6)]

        # 3 - other: red-white
        tiers = (63.72, 51, 42.5, 36.42)
        self.legendTick = dict()
        for i in range(5, 9):
            self.legendTick[i] = [QColor(255, int(255 - k * tiers[i-5]), int(255 - k * tiers[i-5])) for k in range(i)]
            if i > 6:
                #reversed ticks for coup and insurgency indicators
                self.legendTick[-i] = [k for k in reversed(self.legendTick[i])]
        
        # 4 - resource: yellow-orange-red and encyclopedia - green-black
        k = 36.42 #50 for range 5
        self.legendEncyclopedia = [QColor(0, 255 - i * k, 0) for i in range(8)]
        self.legendResrc = [QColor(255, 255 - i * k, 0) for i in range(8)]

        # 5 - war or peace: red or white
        self.legendWarPeace = (QColor(Qt.white), QColor(Qt.red))

        # 6 - events map
        self.legendEvents = (QColor(Qt.white), QColor(Qt.red), QColor(Qt.green), QColor(127, 0, 127), QColor(Qt.blue))


        self.colorSchemeByType = {
            M_DIPL_IN: self.legendDiplo,
            M_DIPL_OUT: self.legendDiplo,
            M_WAR: self.legendWarPeace,
            M_EVENTS: self.legendEvents,
            M_SPHINFL: self.legendSphere,  
        }
        self.redWhiteGradientStepsByType = {M_INSG: 7, M_GOVTSTAB: 8, M_FINLPROB_USA: 5, M_FINLPROB_USSR: 5}
        # The following constatnt is used for creating in-game legend. Each map mode is associated
        # with the set of labels and the set of colors
        s = Local.strings
        self.mapModesLegend = {
            M_SPHINFL: (s[Local.TAG_SPHERE], self.legendSphere),
            M_EVENTS: (s[Local.TAG_EVENT], self.legendEvents),
            M_INSG: (s[Local.TAG_INSURGENCY], self.legendTick[-7]),
            M_GOVTSTAB: (s[Local.TAG_COUP_CHANCE], self.legendTick[-8]),
            M_FINLPROB_USA: (s[Local.FINL_PROB], self.legendTick[5]),
            M_FINLPROB_USSR: (s[Local.FINL_PROB], self.legendTick[5]),
            M_WAR: (s[Local.TAG_WARPEACE], self.legendWarPeace),
            M_DIPL_IN: (s[Local.TAG_RELATION], self.legendDiplo),
            M_DIPL_OUT: (s[Local.TAG_RELATION], self.legendDiplo),
            M_GOVTAID_IN: (s[Local.TAG_POLICY][0:6], self.legendTick[6]),
            M_GOVTINTV_IN: (s[Local.TAG_POLICY][6:12], self.legendTick[6]),
            M_ECONAID: (s[Local.TAG_POLICY][12:18], self.legendTick[6]),
            M_DESTAB: (s[Local.TAG_POLICY][18:24], self.legendTick[6]),
            M_PRESS: (s[Local.TAG_POLICY][24:30], self.legendTick[6]),
            M_TREATY: (s[Local.TAG_POLICY][30:36], self.legendTick[6]),
        }
        for i in (M_GOVTAID_OUT, M_INSGAID_IN, M_INSGAID_OUT):
            self.mapModesLegend[i] = self.mapModesLegend[M_GOVTAID_IN]
        for i in (M_GOVTINTV_OUT, M_INSGINTV_IN, M_INSGINTV_OUT):
            self.mapModesLegend[i] = self.mapModesLegend[M_GOVTINTV_IN]

    def paint(self, mode, addArg):
        """
        Paint countries on the map and set their tooltip labels.
        `mode` - a positive integer, current map mode
        `addArg` - id of a currently selected country that should be painted in the black
                   this argument is used in the international relations map modes only,
                   left None in the other map modes
        
        """
        values = [self.getDisplayedValue(i.id, mode, addArg) for i in self.world.country]
        mean = sum(values) / len(values)
        _max = max(values)
        color = []
        # Discrete coloring - pick color directly from palette, depending on type
        if mode in self.colorSchemeByType:
            color = [self.colorSchemeByType[mode][i] for i in values]
        elif 7 < mode < 22:
            color = [self.legendTick[6][i] for i in values]
        # Resources or encyclopedia - linear gradient
        elif mode > 21:
            for i in values:
                if i > mean:
                    step = (_max - mean) / 127
                    if step == 0: step = 1
                    x = self.assertValue(127 - ((i - mean) / step))
                    color.append(QColor(255, x, 0) if mode < 35 else QColor(0, x, 0))
                else:
                    step = mean / 127
                    if step == 0: step = 1
                    x = self.assertValue(255 - i / step)
                    color.append(QColor(255, x, 0) if mode < 35 else QColor(0, x, 0))
        # Prestige map - linear white-to-red gradient
        elif mode == M_PRESTIGE:
            for i in values:
                if i > mean:
                    step = (_max - mean) / 127
                    x = self.assertValue(127 - ((i - mean) / step))
                    color.append(QColor(255, x, x))
                else:
                    step, x = mean / 127, self.assertValue(255 - i / step)
                    color.append(QColor(255, x, x))
        
        # Others - white-to-red gradient for other maps
        else:
            if mode in self.redWhiteGradientStepsByType:
                step = self.redWhiteGradientStepsByType[mode]
            else: step = 5
            step = 255 / (step - 1)
            for i in values:
                x = 255 - i * step if mode > 4 else i * step
                color.append(QColor(255, x, x))

        if addArg != None: color[addArg] = QColor(Qt.black)

        if mode == M_INSG: print([i.green() for i in color])

        # Set captions
        captions = [""]*len(color)
        if mode in self.mapModesLegend and self.mapModesLegend[0]:
            captions = [self.mapModesLegend[mode][0][i] for i in values]
        elif mode in (M_GNP, 24, 27, 30):
            captions = [Local.formatValue(i, 11) for i in values]
        elif mode in (M_GNPCAP, 25, 28, 31):
            captions = [Local.formatValue(i, 12) for i in values]
        elif mode in (26, 29, 32):
            captions = ['{:.2%}'.format(i) for i in values]
        elif mode == M_POP:
            captions = [Local.formatValue(i, 10) for i in values]
        elif mode == M_MILMEN:
            captions = ['{:,}'.format(i * 1000) for i in values]
        elif mode == M_PRESTIGE:
            captions = ['{:,} %s'.format(i) % Local.strings[Local.UNIT][12] for i in values]
        else:
            captions = ['{:,}'.format(i) + " " \
                + Local.strings[Local.UNIT][ENCYCLOPEDIA_UNITS[mode - 35]] for i in values]
        
        for c,col,caption in zip(self.world.country, color, captions):
            c.mapPolyObject.setColor(col, caption)

    def getDisplayedValue(self, id, mode, addArg):
        """
        Return a value associated with the country of specified `id` and the current map mode (`mode`).
        The international relations map modes require `addArg` to be an id of a source country,
        in the other cases, `addArg` is left None.

        """
        c, actor = self.world.country[id], None
        if addArg != None and mode < 22: actor = self.world.country[addArg]
        # value buffered turn-wise
        if mode in self.buffer:
            return self.buffer[mode][id]
        # value buffered game-wise (encyclopedia data)
        elif mode > 34:
            return c.encyclopedia[mode - 35]
        # non-buffered value
        elif mode == M_WAR:
            return 1 if c.id > 1 and any([i == -127 for i in c.diplOpinion[2:]]) else 0
        elif mode == M_SPHINFL: return c.getSphOfInfluence(self.world)
        elif mode == M_DIPL_OUT: return actor.getDiplOpinionTowards(c)
        elif mode == M_GOVTAID_OUT: return actor.govtAid[id]
        elif mode == M_INSGAID_OUT: return actor.insgAid[id]
        elif mode == M_GOVTINTV_OUT: return actor.govtIntv[id]
        elif mode == M_INSGINTV_OUT: return actor.insgIntv[id]
        elif mode == M_ECONAID: return actor.econAid[id]
        elif mode == M_DESTAB: return actor.destab[id]
        elif mode == M_PRESS: return actor.pressure[id]
        elif mode == M_TREATY: return actor.treaty[id]
        elif mode == M_DIPL_IN: return c.getDiplOpinionTowards(actor)
        elif mode == M_GOVTAID_IN: return c.govtAid[addArg]
        elif mode == M_INSGAID_IN: return c.insgAid[addArg]
        elif mode == M_GOVTINTV_IN: return c.govtIntv[addArg]
        elif mode == M_INSGINTV_IN: return c.insgIntv[addArg]
    
    def recalculateMapBuffer(self):
        """
        This function is used to create a buffer of values that
        do not change during player's turn (for example internal conflicts,
        economic data).

        The buffer update is called at the beginning of the player's each turn.

        """
        world = self.world
        self.buffer = {
            M_EVENTS: [i.getMajorEvents() for i in world.country],
            M_PRESTIGE: [i.prestigeVal // 8 for i in world.country],
            M_INSG: [i.getInsurgency() for i in world.country],
            M_GOVTSTAB: [i.getGovtStability() for i in world.country],
            M_FINLPROB_USA: [i.getCloseUpInfoValue(world, world.USA, 10)[1] for i in world.country],
            M_FINLPROB_USSR: [i.getCloseUpInfoValue(world, world.USSR, 10)[1] for i in world.country],
            M_GNP: [i.getNominalGNP(3) for i in world.country],
            M_GNPCAP: [i.getGNPpcap(3) for i in world.country],
            M_POP: [i.population for i in world.country],
            M_MILMEN: [i.milMen for i in world.country]
        }
        for i in range(3):
            self.buffer[24 + i * 3] = [c.getNominalGNP(i) for c in world.country]
            self.buffer[25 + i * 3] = [c.getGNPpcap(i) for c in world.country]
            self.buffer[26 + i * 3] = [c.gnpFrac[i] / 255 for c in world.country]

    def createLegend(self, selection):
        """
        Create current mapmode legend inside MapView's legend widget."""
        if self.mapMode in self.mapModesLegend:
            m = self.mapModesLegend[self.mapMode]
            if m[0] != None:
                title = Local.strings[Local.MAP_MODE_NAME][self.mapMode]
                if 8 <= self.mapMode <= 21:
                    title += "<br>" + Local.strings[Local.DATA_COUNTRIES + selection.id][Local.CTRY_NAME]
                self.parent.mapView.legendWidget.setLegend(title,m[1],m[0]) #title, colors, captions
        else:
            colors = self.legendResrc if self.mapMode < 35 \
                else self.legendEncyclopedia
            title = Local.strings[Local.MENU][self.mapMode - 4] \
                if self.mapMode >= 35 \
                else Local.strings[Local.MAP_MODE_NAME][self.mapMode]
            self.parent.mapView.legendWidget.setLegend(title, colors, Local.strings[Local.LEGEND][:5])

    def doMapRedraw(self, selection, mapMode):
        self.mapMode = mapMode
        self.paint(mapMode, selection.id if selection != None else None)
        self.createLegend(selection)

    def assertValue(self, x):
        if x < 0: return 0
        elif x > 255: return 255
        return x

    def setWorld(self, world):
        self.world = world