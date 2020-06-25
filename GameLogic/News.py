from constants import *
from math import sqrt
import Local

class News:

    localEventImpt = {0: 5, 1: 14, 2: 10, 3: 2} # importance for different actions inside countries
    intlEventImpt = {   # importance for international policies
        DESTAB: 4,
        ECONAID: 3,
        GOVTAID: 5,
        INSGAID: 5,
        GOVTINTV: 10,
        INGSINTV: 10,
        TREATY: 5
    }
    actionToUnitMode = (3, 2, 0, 0, 1, 1, 4, 5) # Nominal units for various policies quantities

    def __init__(self, target, action, old, new, actor, host, crisisVal):
        super(News, self).__init__()
        self.target = target
        self.actor = actor
        self.host = host
        self.action = action
        self.old, self.new = old, new
        self.crisisVal = crisisVal
        self.isQuestioned = False

        # local events
        if actor == target:
            if action in self.localEventImpt:
                self.importance = self.localEventImpt[action]
            else: self.importance = 5
        # international events
        else:
            if action not in self.intlEventImpt:    #pressure event - special formula
                self.importance = 12 if new > old else 2
            else: self.importance = self.intlEventImpt[action]
        
        self.importance *= (1 + abs(new - old))
        if old > new: self.importance -= 1
        self.importance = int(sqrt((sqrt(actor.prestigeVal * target.prestigeVal) + 1) * self.importance))
        if self.importance < 1: self.importance = 1
        self.setStrings()

    def isEventWithNoValues(self):
        return self.actor == self.target or (self.target.id < 2 and self.action == 0) \
            or (self.actor.id >= 2 and self.target.id >= 2 and self.action == 6)

    def setStrings(self):
        self.text = Local.getNewsHeadline(self.actor, self.host, self.target, self.action, self.old, self.new)

    def getTypeName(self):
        # International events
        if self.actor != self.target:
            # finlandization
            if self.target.id < 2 and self.action == 0:
                return Local.strings[Local.CRISIS_FILTER][16]
            # war - continue or surrender
            elif self.actor.id > 1 and self.target.id > 1 and self.action == 6:
                return Local.strings[Local.CRISIS_FILTER][16 + self.old]
            return Local.strings[Local.MAIN_PANEL][self.action + 16]
        # Internal events
        return Local.strings[Local.CRISIS_FILTER][13 + self.action]

    def getActionValue(self, useOldValue):
        if self.isEventWithNoValues(): return ""
        return Local.parseValue(self.actionToUnitMode[self.action], self.old if useOldValue else self.new)