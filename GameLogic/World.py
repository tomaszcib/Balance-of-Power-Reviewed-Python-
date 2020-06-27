import json
from .Superpower import Superpower
from .Country import Country
from .Globals import mAidConv, intvConv 
from .News import News
from .Crisis import Crisis
import Local
from random import randint

class World:

    def __init__(self, level, twoPlayer, human):
        super(World, self).__init__()
        self.news = []
        self.country = []
        #self.crisis = Crisis()
        self.nastiness = 0
        self.sumDMess = 0
        self.avgDMess = 0
        self.crisis = Crisis()
        self.ANWFlag, self.NWFlag, self.winFlag = False, False, False
        self.newGame(level, twoPlayer, human)
        self.beingQuestioned = False

    def loadWorldData(self):
        with open("data/world_data.json", "r") as f:
            contents = json.load(f)
        # load country basic data
        for i in contents:
            id = i["id"] - 1
            if id < 2:
                self.country.append(Superpower(self, id,
                    Local.strings[Local.DATA_COUNTRIES + id][Local.CTRY_LEADER_NAME],
                    i["gnp"], i["population"], i["milit_spend"], i["govtWing"], i["insgWing"],
                    i["govtStrength"], i["insgStrength"], i["ggrowth"], i["pgrowth"], i["govtStability"],
                    i["investFraction"], i["govtPopularity"], i["militaryMen"], i["dontMess"], i["deaths"]))
            else: self.country.append(Country(self, id,
                    Local.strings[Local.DATA_COUNTRIES + id][Local.CTRY_LEADER_NAME],
                    i["gnp"], i["population"], i["milit_spend"], i["govtWing"], i["insgWing"],
                    i["govtStrength"], i["insgStrength"], i["ggrowth"], i["pgrowth"], i["govtStability"],
                    i["investFraction"], i["govtPopularity"], i["militaryMen"], i["dontMess"], i["deaths"]))
            self.country[-1].languageGroup = i["language_group"]
            # load contingencies and minor influence spheres for the country
            for j in i["contiguous"]: self.country[id].addContingency(j - 1)
            for j in i["minor_sphere"]: self.country[id].addMinorSphere(j - 1)
            self.sumDMess += i["dontMess"]
        self.USA = self.country[0]
        self.USSR = self.country[1]
        # set USA and USSR policies towards countries
        for i in contents:
            id = i["id"] - 1
            for j,k in zip([i["usa_policy"], i["ussr_policy"]], range(2)):
                self.country[k].initPolicies(id, j[1], j[2], j[3], j[4], j[6], j[5])
                self.country[k].diplOpinion[id] = i["usa_opinion" if k == 0 else "ussr_opinion"]
            self.country[id].recalcDiplOpinion(self)
            # set minor country opinions and policies
            for j in i["minor_opinion"]:
                self.country[id].diplOpinion[int(j) - 1] = i["minor_opinion"][j]
            # multipolar level - minor countries can enact policies
            if self.level == 4:
                for j in i["minor_policy"]:
                    x = i["minor_policy"][j]
                    self.country[id].initPolicies(int(j) - 1, x[0], x[1], x[2], x[3])

    def newGame(self, level, twoPlayer, human):
        self.level = level
        self.human = human
        self.cmptr = 1 - human
        self.twoPFlag = twoPlayer
        self.year = 1981
        self.sumDMess = 0
        self.loadWorldData()
        self.loadEncyclopedia()
        self.avgDMess = self.sumDMess // len(self.country)
        self.nastiness = 8 * level + (randint(0,32767) // 2048) #TODO CHANGE RANDINT
        for i in range(2):
            who = self.country[i]
            who.pugnacity = 32 + (4 * level) + (randint(-32767,32767) // 4096)
            who.integrity = 128
            who.adventurousness = who.pugnacity + self.nastiness - who.gnpFrac[2] + 32 - self.country[1-i].pugnacity
            if who.adventurousness < 16: who.adventurousness = 16
        self.country[self.cmptr].pugnacity += (4 * level)
        for c in self.country:
            c.govtWing = self.randomAdjust(c.govtWing, -127, 127, 8192 >> level)
            c.govtStrength = self.randomAdjust(c.govtStrength, 1, 32767, 4096 >> level)
            c.maturity = self.randomAdjust(c.maturity, 0, 255, 8192 >> level)
            c.govtPopul = self.randomAdjust(c.govtPopul, 0, 20, 16384 >> level)
            for i in range(len(self.country)):
                x = c.govtAid[i]
                self.country[i].totalGovtAid += mAidConv(x)
                c.totalGovtAid -= mAidConv(x)
                x = c.insgAid[i]
                c.totalGovtAid -= mAidConv(x)
                x,y = c.govtIntv[i], c.insgIntv[i]
                c.totalIntv += intvConv(x) + intvConv(y)
            x = c.milMen
            tmp = (c.gnpSpnd[2] + c.totalGovtAid) // 2
            if tmp < 1: tmp = 1
            y = sum([(intvConv(c.govtIntv[i.id]) * c.milPower) // c.milMen for i in self.country])
            c.milPower = ((4 * tmp * x) // (tmp + x)) + y
            tmp = c.gnpSpnd[2] // 2
            c.prestigeVal = (16 * tmp * x) // (tmp + x)
            x = (((256 - c.maturity) * c.population)) // 2048
            tmp = sum([2 * mAidConv(c.insgAid[i.id]) for i in self.country])
            if tmp < (x // 8) + 1: tmp = (x // 8) + 1
            c.insgPower = (4 * tmp * x) // (tmp + x)

    def loadEncyclopedia(self):
        """
        The encyclopedia consists of 23 data sets, each data set consists of 80 values
        corresponding to each of the 80 countries in-game. The data are encoded as
        hexadecimal 2-byte integers (= 4 hex characters for each data entry), thus
        each data set is 320 ASCII characters long.

        """
        with open("data/encyclopedia_data.json", "r") as f:
            data = json.load(f)
        # split chunks of data
        for row in data:
            for i in range(len(self.country)):
                self.country[i].encyclopedia.append(int(row[i * 4 : (i + 1) * 4], base=16))
        

    def randomAdjust(self, value, min, max, divisor):
        x = value + randint(-32767,32767) // divisor
        if x < min: x = min
        elif x > max: x = max
        return x

    def addNews(self, actor, target, host, action, old, new, crisis):
        alreadyExists = False
        for n in self.news:
            if n.actor == actor and n.target == target and action == n.action:
                n.new = new
                n.crisisVal = crisis
                n.setStrings()
                alreadyExists = True
                break
        if not alreadyExists:
            self.news.append(News(target, action, old, new, actor, host, crisis))
        self.news.sort(key = lambda x: x.importance, reverse=True)

    def endGame(self, mainWindow):
        # No nuclear war has happened - normal ending
        if self.winFlag and not (self.ANWFlag or self.NWFlag):
            for i in self.country[:2]:
                i.updateScore(self)
                i.oldScore = i.score
                i.historyScore.append(i.score - i.initScore)
            mainWindow.controlPanel.drawScores()
            for i in self.country: i.history.update()
            #TODO scorewindow
        # Nuclear war - bad ending
        else:
            endMsg = Local.strings[Local.WINDOW_ENDGAME][0] \
                % (Local.strings[Local.WINDOW_ENDGAME][1 if self.ANWFlag else 0])
            endMsg = "<font color=\"white\">%s</font>" % endMsg
            mainWindow.lostGameWindow.setText(endMsg)
            mainWindow.lostGameWindow.setVisible(True)
        #TODO Ending procedures

    def changeSides(self):
        if self.human == 0: self.human, self.cmptr = 1, 0
        else: self.human, self.cmptr =  0, 1

    
