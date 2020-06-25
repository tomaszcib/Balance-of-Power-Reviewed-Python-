
class Crisis:

    def __init__(self):
        super(Crisis, self).__init__()
        self.resetCrisisData()

    def resetCrisisData(self):
        self.sumLoser = 0
        self.sumWinner = 0
        self.level = 0
        self.savHuman = 0
        self.base = 0
        self.hloss = 0
        self.cgain = 0
        self.daol = 0
        self.daow = 0
        self.Usex = 0
        self.rand1 = 0
        self.rand2 = 0
        self.Usez = 0
        self.tmp = 0
        self.backDown = False
        self.aggrFlag = False
        self.hasBegun = False
        self.whichHead = None
        self.who = None
        self.victim = None
        self.usaImpt = 0
        self.ussrImpt = 0