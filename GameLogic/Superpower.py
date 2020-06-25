from .Country import Country
from .Globals import mAidConv, intvConv

class Superpower(Country):
    """
    Class representing the Superpowers - playable countries that can enact variety
    of policies. Every superpower has also several additional properties:
    - historic, original and current in-game score,
    - pugnacity, adventuroussness and integrity parameters that affect AI behavior
      and how the superpower is seen by the international community.
    """

    def __init__(self, parent, id, leaderName, GNP, pop, milSpnd, govtWing, insgWing,
                govtStrength, insgStrength, gGrowth, pGrowth, govtStability, invtFrac,
                govtPopul, milMen, dMess, deaths):
        super().__init__(parent, id, leaderName, GNP, pop, milSpnd, govtWing, insgWing,
                govtStrength, insgStrength, gGrowth, pGrowth, govtStability, invtFrac,
                govtPopul, milMen, dMess, deaths)
        self.pugnacity = 0
        self.adventurousness = 0
        self.integrity = 0
        self.econAid = [0]*80
        self.destab = [0]*80
        self.treaty = [0]*80
        self.pressure = [0]*80
        self.oldEconAid = [0]*80
        self.oldDestab = [0]*80
        self.oldTreaty = [0]*80
        self.oldPressure = [0]*80
        self.historyScore = []
        self.initScore, self.oldScore, self.score = 0, 0, 0

    def initPolicies(self, target, govtAid, insgAid, govtIntv, insgIntv, econAid, treaty):
        super().initPolicies(target, govtAid, insgAid, govtIntv, insgIntv)
        self.econAid[target] = econAid
        self.treaty[target] = treaty
    
    def setMaxPolicy(self):
        self.maxIntervene = self.maxMilAid = 5
        for i in range(4, -1, -1):
            if mAidConv(i + 1) > (self.gnpSpnd[2] // 8) + self.totalGovtAid:
                self.maxMilAid = i
            if intvConv(i + 1) > (self.milMen // 4) - self.totalIntv:
                self.maxIntervene = i

    def updateScore(self, world):
        self.score = sum([self.diplOpinion[c.id] * c.prestigeVal for c in world.country]) // 1024