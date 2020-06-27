from GameLogic.Globals import *
from GameLogic.MovePlanner import continueNextTurn
from random import randint
import Local

def getAdvisorOpinion(world, news, bias, **kwargs):
    """
    Get advisor opinion whether the news should be a matter of international escalation
    or not. bias is an integer between 1 and 4 - represents different advisor's opinion.
    """
    if "reversed" in kwargs and kwargs["reversed"]: factor = -1
    else: factor = 1
    x = factor * gimpt(world, news.actor, news.action, news.target, news.old, news.new, bias)
    x //= 8
    x += 1
    if x < -15: x = -15
    elif x > 16: x = 16
    return Local.strings[Local.ADVISORY][x - 1]

def reactNews(mainWindow, world):
    """Superpower AI decides which policies it reacts to"""
    for n in world.news:
        if n.action in (INGSINTV,INSGAID,DESTAB,PRESSURE) and n.actor.id < 2:
            world.nastiness += (n.new - n.old)
            if world.nastiness < 1: world.nastiness = 1
            elif world.nastiness > 127: world.nastiness = 127
        # Computer-human crisis
        if n.actor.id == world.human and n.new > n.old and not world.twoPFlag and not n.crisisVal:
            x = -gimpt(world, n.actor, n.action, n.target, n.old, n.new, 0)
            y,z = world.crisis.usaImpt, world.crisis.ussrImpt
            if world.cmptr == 0: z = y
            if z < 0: x = 256
            n.isQuestioned = (x < abs((randint(-32767,32767) // 1024)))
        # Computer questions minor countries
        elif n.actor.id > 1 and n.new > n.old and not world.twoPFlag \
            and influence(world.country[world.cmptr], n.actor) > 3:
            x = -gimpt(world, n.actor, n.action, n.target, n.old, n.new, 0)
            y,z = world.crisis.usaImpt, world.crisis.ussrImpt
            if world.cmptr == 0: z = y
            if z > abs(randint(-32767,32767) // 1024): computerCrisis(world, n)
        
    # Begin process of questioning by the computer
    for n in world.news:
        if n.isQuestioned:
            world.beingQuestioned = True
            mainWindow.newsWindow.showUp()
            #doCrisis(mainWindow.newsWindow, world, n)
            return
    continueNextTurn(mainWindow, world)

def hangLoose(newsWindow, world, loser, winner, victim):
    """
    `loser` backs down in the crisis between superpowers.
    Both `loser` and `winner` are assumed to be Superpower objects,
    whereas `victim` is a Country object.
    """
    crisis = world.crisis
    n = crisis.whichHead
    n.isQuestioned = False
    if crisis.level < 8:
        # No penalty for early withdrawal
        winner.pugnacity += ((130 - winner.pugnacity) // 4)
        x = loser.treaty[victim.id]
        t = impt(loser, victim, n.action, n.old, n.new)
        loser.integrity -= ((2 * should(x) * t) // 256)
        if loser.integrity < 1: loser.integrity = 1
        elif loser.integrity > 127: loser.integrity = 127
        y = gimpt(world, crisis.who, n.action, n.target,
            n.old, n.new, 0)
        t,z = crisis.usaImpt, crisis.ussrImpt
        x,y = (abs(t) // crisis.level) + (abs(z) // crisis.level) + 8 - crisis.level, 0
        for c in world.country[2:]:
            z,y = x // 32, y + x % 32
            if y > 32: z, y = z + 1, y - 32
            changeDiplOpinion(c, loser, -z)
            changeDiplOpinion(c, winner, z)
    if crisis.level % 2 == 1:
        x = n.new
        n.new = n.old
        n.old = x
        n.crisisVal = True
        if crisis.who.id == world.cmptr:
            doPolicy(world, n.actor, n.target, n.action, n.new, crisis=True)
        #else: print("TODO")
    else: n.crisisVal = True
    x = 9 - crisis.level
    if x > victim.dMess: x = victim.dMess
    if loser.id == 0: x = -x
    changeDMess(world, victim, x)
    newsWindow.reactionLine.setText(Local.generateReactionLine(loser, crisis.level, False, True))
    newsWindow.question.setEnabled(False)
    newsWindow.backDown.setText(Local.strings[Local.CRISIS_BD_BUTTON][1])

def hangTough(newsWindow, world, actor):
    """
    `actor` toughens the crisis between the two superpowers.
    `actor` is a participant in the crisis, thus a Superpower object.
    """
    crisis = world.crisis
    n = crisis.whichHead
    victim = crisis.victim
    crisis.level -= 1
    if crisis.level < 7:
        newsWindow.setWindowTitle(Local.strings[Local.CRISIS_FILTER][21 if crisis.level < 5 else 20])
    x = actor.treaty[victim.id]
    y = impt(actor, victim, n.action, n.old, n.new)
    actor.integrity += ((should(x) * y) // 256)
    if actor.integrity < 1: actor.integrity = 1
    elif actor.integrity > 127: actor.integrity = 127
    changeDiplOpinion(world.country[world.cmptr], world.country[world.human], crisis.level - 9)
    x = 0
    if crisis.level == 2: x = 16
    elif crisis.level == 3: x = 8
    elif crisis.level == 4: x = 2
    if world.USA.diplOpinion[1] > 0: x = 0
    else: x = (x * (-world.USA.diplOpinion[1])) // 64
    y = randint(-32767,32767) // 128
    # Accidental nuclear war has been triggered - end of the game
    if x > abs(y): crisis.level, world.ANWFlag = 1, True
    world.nastiness += 9 - crisis.level
    # End of the game, nuclear war has been ignited
    if crisis.level == 1:
        world.NWFlag = True
        newsWindow.reactionLine.setText("")
        newsWindow.setVisible(False)
        world.beingQuestioned = False
        #world.quitFlag = True
        newsWindow.parent.endGame()
    newsWindow.reactionLine.setText(Local.generateReactionLine(actor, crisis.level, False, False))

def doCrisis(newsWindow, world, headline):
    """Main human vs superpower AI crisis routine"""
    c = world.crisis
    if not c.hasBegun:
        c.resetCrisisData()
        c.hasBegun, c.whichHead, c.who = True, headline, headline.actor
        c.victim, c.level, c.backDown = headline.target, 9, False
        c.rand1, c.rand2 = randint(-32767,32767), randint(-32767,32767)
        c.aggrFlag = c.who.id == world.cmptr
        if c.aggrFlag:
            c.x = (world.human == 1 if world.human == 0 else -1)
            changeDMess(world, c.victim, c.x)
        newsWindow.setWindowTitle(Local.strings[Local.CRISIS_FILTER][19])
        newsWindow.reactionLine.setText(Local.generateReactionLine(
            world.country[1-c.who.id], c.level, False, False))
        newsWindow.backDown.setEnabled(True)
        newsWindow.backDown.setText(Local.strings[Local.CRISIS_BD_BUTTON][0])
        newsWindow.question.setEnabled(True)
        newsWindow.setLocked(True)
        if c.who.id == world.human:
            # Create advisory panel
            for i in range(4):
                newsWindow.advice[i].setText(getAdvisorOpinion(world, headline, i + 1, reversed=True))
                newsWindow.picture[i].setVisible(True)
            newsWindow.newsHline.setText(headline.text)
            newsWindow.setVisible(True)
    
    # Computer considerations
    if c.aggrFlag and not world.twoPFlag:
        c.x = gimpt(world, c.who, headline.action, c.victim, headline.old, headline.new, 0)
        c.hloss, c.cgain = c.usaImpt, c.ussrImpt
        if c.who.id == world.human: c.x = -c.x
        # Decide to toughen the crisis
        if c.x < 4 * c.level - 36 + abs(randint(-32767,32767) // 1024):
            hangTough(newsWindow, world, world.country[world.cmptr])
        # Decide to back down
        else:
            c.backDown, c.hasBegun, headline.crisisVal = True, False, True
            hangLoose(newsWindow, world, world.country[world.cmptr],
                world.country[world.human], c.victim)
    # Calculate possible penalties for withdrawal
    if not c.backDown and c.level > 1:
        c.sumLoser = c.sumWinner = 0
        # No penalty for early withdrawal
        c.hloss = gimpt(world, c.who, headline.action, c.victim, headline.old, headline.new, 0)
        c.y, c.z = c.usaImpt, c.ussrImpt
        c.x = (abs(c.y) // c.level) + (abs(c.z) // c.level) + 8 - c.level
        c.y = 0
        # Calculate the penalty
        for i in world.country[2:]:
            c.Usez, c.y = c.x // 32, c.y + c.x % 32
            if c.y > 32: c.Usez, c.y = c.Usez + 1, c.y - 32
            c.Usex = -c.Usez
            c.daow = i.diplOpinion[world.cmptr]
            c.daol = i.diplOpinion[world.human]
            if c.daol + c.Usex > 127: c.Usex = 127 - c.daol
            if c.daol + c.Usex < -127: c.Usex = -127 - c.daol
            if c.daow + c.Usez > 127: c.Usez = 127 - c.daow
            if c.daow + c.Usez < -127: c.Usez = -127 - c.daow
            c.sumWinner += (c.Usez * i.prestigeVal)
            c.sumLoser += (c.Usex * i.prestigeVal)
        if c.sumLoser > 8132352: c.sumLoser =  8132352
        elif c.sumLoser < -8132352: c.sumLoser = -8132352
        c.hloss, c.cgain = -(c.sumLoser // 1024), -(c.sumWinner // 1024)
        # Prestige at risk
        newsWindow.setRiskValuesVisible(True)
        newsWindow.leftInfoVal[0].setText(str(c.hloss))
        c.y = (2048, 1024, 512, 512)[world.level - 1]
        c.x = gimpt(world, c.who, headline.action, c.victim, headline.old, headline.new, 0)
        c.hloss, c.cgain = c.usaImpt, c.ussrImpt
        c.x = abs((c.hloss + (c.rand1 // c.y)) // 16)
        if c.x > 7: c.x = 7
        newsWindow.leftInfoVal[1].setText(Local.strings[Local.CRISIS_RISK][c.x])
        c.x = abs((c.cgain + (c.rand2 // c.y)) // 16)
        if c.x > 7: c.x = 7
        newsWindow.leftInfoVal[2].setText(Local.strings[Local.CRISIS_RISK][c.x])
    newsWindow.question.setText(Local.strings[Local.CRISIS_SUPER_BUTTON][c.level-1])
    c.aggrFlag = True

def minorTough(newsWindow, world):
    """
    Toughen the human vs minor country AI crisis.
    Can be executed by both of the parties.
    """
    c = world.crisis
    c.level -= 1
    x = 128 >> c.level
    # Worsen diplomatic relations
    changeDiplOpinion(c.who, world.country[world.human], -x)
    newsWindow.reactionLine.setText(Local.generateReactionLine(c.who, c.level, True, False))

    # Minor countries will never escalate into nuclear war
    if c.level < 2:
        c.backDown, c.hasBegun = True, False
        newsWindow.reactionLine.setText(Local.generateReactionLine(c.who, c.level, True, True))
        newsWindow.question.setEnabled(False)
        newsWindow.backDown.setText(Local.strings[Local.CRISIS_BD_BUTTON][1])
    newsWindow.question.setText(Local.strings[Local.CRISIS_MINOR_BUTTON][c.level-1])

def minorCrisis(newsWindow, world, news):
    """Main human vs minor country AI crisis routine"""
    c = world.crisis
    # If crisis hasn't begun yet, start it now
    if not c.hasBegun:
        c.resetCrisisData()
        c.hasBegun, c.whichHead = True, news
        c.who, c.victim, c.level = news.actor, news.target, 9
        c.backDown = False
        c.x = (1, -1)[world.human]
        newsWindow.setLocked(True)
        newsWindow.backDown.setEnabled(True)
    c.x = abs(c.victim.dMess - world.avgDMess) * influence(world.country[world.human], c.victim)
    c.y = 1 << ((9 - c.level) // 2)
    # Minor AI toughens the crisis
    if c.x * c.y < 4 * c.level - 36 + abs(randint(-32767,32737) // (c.y * 256)):
        minorTough(newsWindow, world)
    # Minor AI backs down
    else:
        c.backDown, c.hasBegun, c.whichHead.crisisVal = True, False, True
        doPolicy(world, c.who, c.victim, news.action, news.old, crisis=True)
        newsWindow.reactionLine.setText(Local.generateReactionLine(c.who, c.level, True, True))
        newsWindow.question.setEnabled(False)
        newsWindow.backDown.setText(Local.strings[Local.CRISIS_BD_BUTTON][1])

def tough(world):
    """
    Toughen superpower AI vs minor country AI crisis.
    Can be executed by both of the parties.
    """
    c = world.crisis
    c.level -= 1
    x = 128 >> c.level
    changeDiplOpinion(c.who, world.country[world.cmptr], -x)

def computerCrisis(world, news):
    """Main superpower AI vs minor country AI crisis routine"""
    c = world.crisis
    c.whichHead = news
    c.who, c.victim = news.actor, news.target
    c.level, c.x = 9, (1,-1)[world.cmptr]
    changeDMess(world, c.victim, c.x)
    while True:
        c.x = (abs(c.victim.dMess - world.avgDMess) * influence(world.country[world.cmptr], c.who)) // 8
        c.y = 1 << ((9 - c.level) // 2)
        # Minor country toughens the crisis
        if c.x * c.y < 4 * c.level - 36 * abs(randint(-32767,32767) // (c.y * 256)):
            tough(world)
        # Minor country back down
        else:
            c.backDown, news.crisisVal = True, True
            doPolicy(world, c.who, c.victim, news.action, news.old, crisis=True)
        # Superpower considerations
        if not c.backDown and c.level > 1:
            c.x = gimpt(world, c.who, news.action, c.victim, news.old, news.new, 0)
            c.y, c.z = c.usaImpt, c.ussrImpt
            if world.cmptr == 0: c.z = c.y
            # Toughen the crisis
            if c.z > 4 * c.level - 36 * abs(randint(-32767,32767) // 1024):
                tough(world)
            # Back down
            else: c.backDown = news.crisisVal = True
        if not (not c.backDown and c.level > 1): return

def doCHumanLoose(newsWindow, world, news):
    """
    Human player decides to back down (in a crisis of any type).
    Action performed on clicking the 'back down' button in the NewsWindow.
    """
    c = world.crisis
    # Crisis against superpower AI
    if c.who.id < 2:
        # First click - do the back down
        if not c.backDown:
            c.backDown, c.hasBegun = True, False
            hangLoose(newsWindow, world, world.country[world.human],
                world.country[world.cmptr], news.target)
            if world.twoPFlag: world.changeSides()
        # Click one more time to exit
        else:
            newsWindow.setLocked(False)
            if world.beingQuestioned:
                if len(newsWindow.news) == 0:
                    world.beingQuestioned = False
                    newsWindow.setVisible(False)
                    continueNextTurn(newsWindow.parent, world)
                else: doCrisis(newsWindow, world, newsWindow.news[0])
    # Crisis against minor country
    else:
        # First click - do the back down
        if not c.backDown:
            c.backDown, c.hasBegun = True, False
            newsWindow.reactionLine.setText(Local.generateReactionLine(world.country[world.human],
                c.level, True, True))
            newsWindow.question.setEnabled(False)
            newsWindow.backDown.setText(Local.strings[Local.CRISIS_BD_BUTTON][1])
        # Click one more time to exit
        else:
            newsWindow.setLocked(False)
    #TODO draw scores


def doCHumanTough(newsWindow, world, news):
    """
    Human player toughens a crisis (of any type).
    Action performed on clicking the 'question' button in the NewsWindow.
    """
    c = world.crisis
    # Crisis against superpower AI
    if news.actor.id < 2:
        if (c.level < 9 and c.hasBegun) or (c.level == 9 and c.who.id == world.human and c.hasBegun):
            hangTough(newsWindow, world, world.country[world.human])
        if not world.ANWFlag and not world.NWFlag:
            doCrisis(newsWindow, world, news)
            # TODO display window
        if world.twoPFlag: world.changeSides()
    # Crisis against minor country
    else:
        if c.level < 9 and c.hasBegun:
            minorTough(newsWindow, world)
        minorCrisis(newsWindow, world, news)
        # TODO SHow window
