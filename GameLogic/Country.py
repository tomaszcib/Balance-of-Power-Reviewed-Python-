from .Globals import *
from .History import History
from random import choice
import Local

class Country:

    def __init__(self, parent, id, leaderName, GNP, pop, milSpnd, govtWing, insgWing,
                govtStrength, insgStrength, gGrowth, pGrowth, govtStability, invtFrac,
                govtPopul, milMen, dMess, deaths):
        self.parent = parent
        self.diplOpinion = [0]*80
        self.minorSphere = [False]*80
        self.contig = [False]*80
        self.govtAid = [0]*80
        self.insgAid = [0]*80
        self.govtIntv = [0]*80
        self.insgIntv = [0]*80
        self.finlProb = [0]*2
        self.oldGovtAid = [0]*80
        self.oldInsgAid= [0]*80
        self.oldInsgIntv = [0]*80
        self.oldGovtIntv = [0]*80
        self.oldFinlProb = [0]*2
        self.gnpSpnd = [0]*3
        self.gnpFrac = [0]*3
        self.milPressure = 0
        self.hasFinland = [False]*2

        self.id = id
        self.languageGroup = 0
        self.name = leaderName
        self.leaderName = leaderName
        self.oldLeaderName = ""
        GNP //= 2; milSpnd //= 2
        self.population = pop
        self.GNP = GNP
        self.gnpSpnd[2] = milSpnd
        self.milMen = milMen
        self.draftFrac = (milMen * 255) // pop
        self.govtWing = govtWing
        self.insgWing = insgWing
        self.govtStrength = govtStrength
        self.insgStrength = insgStrength
        self.hasRevolution = self.hasCoup = False

        self.gnpFrac[2] = ((255 * milSpnd) // 10) // GNP
        self.gnpFrac[1] = invtFrac
        self.gnpFrac[0] = 255 - self.gnpFrac[1] - self.gnpFrac[2]
        self.govtPopul = 10 + (128 - abs(govtWing)) // 8
        self.oldGovtPopul = 0
        for i in range(2):
            self.gnpSpnd[i] = (self.gnpFrac[i] * GNP) // 256
        
        self.dMess = dMess
        self.maturity = 256 - (deaths // pop)
        if self.maturity < 0: self.maturity = 0
        self.prestigeVal = 0
        self.strengthRatio = 0
        self.oldGovtStrength = 0
        self.oldInsgStrength = 0
        self.totalIntv = 0
        self.totalGovtAid = 0
        self.milPower = 0
        self.coupGain = [0,0]
        self.revlGain = [0,0]
        self.finlGain = [0,0]
        self.encyclopedia = []
        self.mapPolyObject = None
        self.history = History(self)
        self.localNews = ""
        self.localNewsAtWarWith = None
        self.localNewsSurrender = None

    def recalcDiplOpinion(self, world):
        id = self.id
        for i in range(80):
            self.diplOpinion[i] = ((world.USA.diplOpinion[id] * world.USA.diplOpinion[i]) // 256)\
                + ((world.USSR.diplOpinion[id] * world.USSR.diplOpinion[i]) // 256)

    def addContingency(self, target):
        """
        Mark target country as contiguous to self

        """
        self.contig[target] = True
        self.addMinorSphere(target)

    def addMinorSphere(self, target):
        """
        Add target country as a part of the sphere of interest of self.

        """
        self.minorSphere[target] = True

    def initPolicies(self, target, govtAid, insgAid, govtIntv, insgIntv):
        self.govtAid[target] = govtAid
        self.insgAid[target] = insgAid
        self.govtIntv[target] = govtIntv
        self.insgIntv[target] = insgIntv

    def generateNewLeader(self):
        self.oldLeaderName = self.leaderName
        self.leaderName = choice(Local.strings[Local.DATA_LANGUAGES][self.languageGroup].split("*"))

    def getCloseUpInfoValue(self, world, s, type):
        dipl = s.diplOpinion[self.id]
        maxNum, old, mode,max = 0,0,0,0
        # Dipl relationship
        if type == 0:
            max, val, mode = 127, dipl, 8
        # prestige
        elif type == 1:
            val = (dipl * self.prestigeVal // 1024)
        # military aid
        elif type == 2:
            val, max = s.govtAid[self.id], milMax(dipl)
            if s.maxMilAid < max: max = s.maxMilAid
            old, mode = s.oldGovtAid[self.id], 0
        # insg aid
        elif type == 3:
            val, max = s.insgAid[self.id], s.maxMilAid
            x = getMaxLevel((512,128,32,8,1), self.strengthRatio, lt=True)
            if x < max: max = x
            x = insgAidMax(world, s, self)
            if x < max: max = x
            old, mode = s.oldInsgAid[self.id], 0
        # govt intervene
        elif type == 4:
            val, x, old, mode = s.govtIntv[self.id], s.treaty[self.id], s.oldGovtIntv[self.id], 1
            max = intvGovtMax(world.level, x, dipl)
            if s.maxIntervene < max: max = s.maxIntervene
        # insg intervene
        elif type == 5:
            val, old, max, x = s.insgIntv[self.id], s.oldInsgIntv[self.id], s.maxIntervene, intvInsgMax(world, s, self)
            if x < max: max = x
            mode = 1
        # econ aid
        elif type == 6:
            val, old, max, = s.econAid[self.id], s.oldEconAid[self.id], econAidMax(dipl)
            aidSum = sum([econConv(i) for i in s.econAid[2:]])
            x, y = 5, (s.GNP // 44) - (2 * aidSum)
            for k in range(4, -1, -1):
                if econConv(k + 1) > y: x = k
            if x < max: max = x
            mode = 2
        # destabilization
        elif type == 7:
            val, old, max, mode = s.destab[self.id], s.oldDestab[self.id], 5, 3
        # pressure
        elif type == 8:
            val, old, max, mode = s.pressure[self.id], s.oldPressure[self.id], 5, 4
        # treaty
        elif type == 9:
            val, old, mode = s.treaty[self.id], s.oldTreaty[self.id], 5
            max = treatyMax(world.level, s.integrity + dipl - s.pugnacity)
        # finl. probability
        elif type == 10:
            val = 0
            old = val
            y = self.finlProb[s.id]
            if y > 31: val = (y - 8) // 24
            maxNum, max, old, mode = 4, 99, val, 6
        # finl annual change
        elif type == 11:
            y = self.finlProb[s.id] - self.oldFinlProb[s.id]
            val = (y + 18) // 4
            old, maxNum, max, mode = val, 9, 99, 7
        return mode, val, old, maxNum, max

    def getInsurgency(self):
        """Get insurgency on a scale from 0 to 5."""
        return getMaxLevel((1,7,31,127,511,2047), self.strengthRatio)
    
    def getInsurgencyChange(self):
        """Check if ingurgency is growing or decreasing."""
        val = (self.govtStrength // ((self.insgStrength // 5) + 1))\
            - (self.oldGovtStrength // ((self.oldInsgStrength // 5) + 1))
        return (1 if val >= 1 else 0)
    
    def getIdeology(self, who):
        """Get government or insurgents ideology."""
        x = self.govtWing if who == "govt" else self.insgWing
        return (x + 128) // 16
    
    def getMilPower(self):
        """Get military might on a scale from 0 to 6"""
        return getMaxLevel((20,40,100,200,500,1000,2000), self.milPower)
    
    def getDiplOpinionTowards(self, c):
        """Get diplomatic opinion towards country c on a scale from 0 to 7"""
        return getMaxLevel((-100,-72,-44,-16,16,44,62,100), self.diplOpinion[c.id])

    def getSphOfInfluence(self, world):
        """Get sphere of influence of self on a scale from 0 (more USA) to 12 (more USSR)"""
        val = (((self.dMess - world.avgDMess) * 8) // world.avgDMess) + 6
        if val > 12: val = 12
        if val < 0: val = 0
        return val

    def getGovtStability(self):
        """Get government stability on scale from 0 to 7"""
        val = self.govtPopul // 2
        return (7 if val > 7 else val)

    def getGovtStabilityChange(self):
        """Get government stability change on a scale from 0 to 5"""
        val = 3 + self.govtPopul - self.oldGovtPopul
        return (5 if val > 5 else val)

    def getFinlizProb(self, s):
        """Get finlandization probability towards superpower s on a scale from 0 to 4"""
        y = self.finlProb[s.id]
        if y > 31: val = (y - 8) // 24
        return (4 if val > 4 else val)

    def getMajorEvents(self):
        """
        Check if any of the major events has happened inside the country.
        Only the event with the highest priority is returned
        """
        if self.hasRevolution: return 1
        elif self.hasCoup: return 2
        elif self.hasFinland[0]: return 3
        elif self.hasFinland[1]: return 4
        return 0

    def isAtWarWithAnyone(self, world):
        """Check if self is at war with any other country"""
        if self.id < 2: return 0
        for k in world.country[2:]:
            if k.diplOpinion[self.id] == -127: return 1
        return 0

    def getAvailableAid(self):
        return 2 * ((self.gnpSpnd[2] // 8) + self.totalGovtAid)
    
    def getAvailableMen(self):
        return (self.milMen // 4) - self.totalIntv
    
    def getNominalGNP(self, sector):
        """
        Get nominal Gross National Product by sector
        (0 - consumer, 1 - investment, 2 - military or 3 - sum of all 3 sectors)
        """
        #if sector == 3: return (sum(self.gnpSpnd[:2])) * 2 + self.gnpSpnd[2] // 10
        #elif sector == 2: return self.gnpSpnd[2] // 10
        #else: return self.gnpSpnd[sector] * 2
        
        #if sector == 3:
        #    x = sum([i / 255 * self.GNP * 2 for i in self.gnpFrac[:2]])
        #        + self.gnpFrac[2] 
        #    return round(sum([self.gnpFrac[i] / 255 * self.GNP * 2 for i in range(3)]), 2)
        #else: return round(self.gnpFrac[sector] / 255 * self.GNP, 2)
        if sector == 3: return round(sum([self.getNominalGNP(i) for i in range(3)]), 2)
        elif sector == 2: return round(self.gnpFrac[2] * self.GNP // 255, 2)
        else: return round(self.gnpFrac[sector] * self.GNP // 255 * 2, 2)
        
        #else: return self.gnpSpnd[sector] * (0.1 if sector == 2 else 2)

    def getGNPpcap(self, sector):
        """Get GNP per capita of sector"""
        return self.getNominalGNP(sector) * 1000 // self.population
    
    def getInsurgentsName(self):
        """Get name of the currently operating insurgent group"""
        return Local.strings[Local.DATA_COUNTRIES + self.id][6 if self.insgWing < 0 else 7]

    def generateLocalNews(self):
        """Generate local news string. The local news are displayed in the close-up window"""
        self.localNews =  "<li>"
        count = 0
        tmp = "<ul>%s</ul>"
        if self.localNewsAtWarWith:
            self.localNews += tmp % Local.getNewsHeadline(self, self, self.localNewsAtWarWith, 6, 2, 1)
            count += 1
        if self.localNewsSurrender:
            self.localNews += tmp % Local.getNewsHeadline(self, self, self.localNewsSurrender, 6, 1, 1)
            count += 1
        if self.hasRevolution:
            z = self.insgWing
            self.localNews += tmp % Local.getNewsHeadline(self, self, self, 1, 4 + 1 if z >= 0 else 0, 1 if z >= 0 else 0)
            count += 1
        if self.hasCoup:
            self.localNews += tmp % Local.getNewsHeadline(self, self, self, 2, 0, (self.maturity // 64) + 1)
            count += 1
        for i in range(2):
            if self.hasFinland[i]:
                self.localNews += tmp % Local.getNewsHeadline(self, self, self.parent.country[i], 0, 0, 0)
                count += 1
        if count < 1: self.localNews += tmp % Local.generateFirstHead(self)
        if count < 2: self.localNews += tmp % Local.generateLastHead(self)
        self.localNews += "</li>"

    def __getstate__(self):
        """Function used while pickling the Country during game saving. Exclude mapPolyObject"""
        return dict((k, v) for (k, v) in self.__dict__.items() if k != "mapPolyObject")

    
    