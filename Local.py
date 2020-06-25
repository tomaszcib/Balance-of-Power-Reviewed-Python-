import json
import random
from GameLogic.Globals import getMaxLevel

MAP_MODE_NAME           = 0
TAG_RELATION            = 1
TAG_POLICY              = 2
FINL_PROB               = 3
TAG_INSURGENCY          = 4
TAG_SPHERE              = 5
LEGEND                  = 6
UNIT                    = 7
WINDOW_INFO             = 8
TAG_IDEOLOGY            = 9
TAG_STREMGTH            = 10
TAG_COUP_CHANCE         = 11
TAG_COUP_PACE           = 12
TAG_INSG_PACE           = 13
TAG_EVENT               = 14
CRISIS_FILTER           = 15
ADVISORY                = 16
LABEL_POLICY            = 17
WINDOW_HISTORY          = 18
WINDOW_HISTORY_LEGEND   = 19
WINDOW_NEWGAME          = 20
CRISIS_RISK             = 21
FINL_PACE               = 22
CRISIS_SUPER_BUTTON     = 23
CRISIS_MINOR_BUTTON     = 24
CRISIS_BD_BUTTON        = 25
CRISIS_STR              = 26
WINDOW_ECONOMY          = 27
EVENT                   = 28
MENU                    = 29
WINDOW_SCORES           = 30
WINDOW_ENDGAME          = 31
WINDOW_PROGINFO         = 32
WINDOW_POLICY           = 33
TAG_WARPEACE            = 34
MAIN_PANEL              = 35
DATA_LANGUAGES          = 36
DATA_COUNTRIES          = 37
CTRY_NAME               = 0
CTRY_ADJECTIVE          = 1
CTRY_GENITIVE           = 2
CTRY_CAPITAL            = 3
CTRY_LEADER_TITLE       = 4
CTRY_LEADER_NAME        = 5
CTRY_INSG_LEFT          = 6
CTRY_INSG_RIGHT         = 7

def getLanguage(language):
    global strings
    with open("data/local/" + language + ".json") as f:
        return json.load(f)

strings = getLanguage("english")["data"]

_howManyStrings = (
    (3,3,4,4,4,4,3,4),
    (3,4,3,4,3,4,2,4),
    (0,0,3,3,2,4,3,3,2,2),
    (0,0,3,2,3,3,3,2,3,2),
    (4,)*10,
    (4,)*10)
_startingAt = (
    (16,19,29,40,48,58,66,69),
    (81,22,33,44,52,62,84,73),
    (0,0,21,18,16,12,9,6,4,2),
    (0,0,41,39,36,36,31,29,26,24),
    (0,0,56,56,52,52,48,48,44,44),
    (60,)*10)
# units for different map modes or value types
_modeUnits = {
    6: FINL_PROB,
    7: FINL_PACE,
    9: TAG_SPHERE,
    10: TAG_INSURGENCY,
    11: TAG_COUP_CHANCE,
    12: TAG_EVENT,
    13: TAG_RELATION,
    14: TAG_WARPEACE,
}


def getNewsHeadline(actor, host, victim, action, old, new):
    global strings
    toReturn = ""
    # internal events
    if actor == host:
        if action == 1 and victim == actor: a,b = 0,3
        elif action == 0 and victim.id < 2: a,b, = 3,4
        elif action == 2 and victim == actor: a,b = 13,3
        elif action == 6 and old == 2: a,b = 7,3
        elif action == 6 and old == 1: a,b = 10,3
        elif action == 1 and victim.id < 2: a,b = 26,3
        elif action == 2 and victim.id < 2: a,b = 36,4
        elif action == 4 and victim.id < 2: a,b = 55,3
        elif action == 7 and victim.id < 2: a,b = 77,4
        elif action == 5: a,b = old,4
        startingAt, howManyStrings = a, b
    # policy events
    else:
        group = 0 if new > old else 1
        startingAt, howManyStrings = _startingAt[group][action], _howManyStrings[group][action]

    # concatenate the headline composed with 2 or more subparts
    for i in range(startingAt, startingAt + howManyStrings):
        strPart = strings[EVENT][i].split("*")
        type = int(strPart[0]) 
        # first character indicates which substring will be used as a subpart
        if type == 0: skip = random.randint(0,3)
        elif type == 1: skip = new
        elif type == 3: skip = 0
        elif type == 4: skip = old
        # append the part
        toReturn += strPart[1:][skip]
    # replace the special characters with other data
    victimStr, actorStr = strings[DATA_COUNTRIES + victim.id], strings[DATA_COUNTRIES + actor.id]
    toReturn = toReturn.replace("_", victimStr[CTRY_NAME])
    toReturn = toReturn.replace("=", victimStr[CTRY_ADJECTIVE])
    toReturn = toReturn.replace("&", victimStr[CTRY_LEADER_TITLE])
    toReturn = toReturn.replace("{", victim.leaderName)
    toReturn = toReturn.replace("[", victim.oldLeaderName)
    toReturn = toReturn.replace("@", victimStr[CTRY_CAPITAL])
    toReturn = toReturn.replace("|", victimStr[CTRY_GENITIVE])
    toReturn = toReturn.replace("!", actorStr[CTRY_NAME])
    toReturn = toReturn.replace(">", actorStr[CTRY_ADJECTIVE])
    toReturn = toReturn.replace("+", actorStr[CTRY_LEADER_TITLE])
    toReturn = toReturn.replace("}", actor.leaderName)
    toReturn = toReturn.replace("]", actor.oldLeaderName)
    toReturn = toReturn.replace("^", actorStr[CTRY_CAPITAL])
    toReturn = toReturn.replace("?", actorStr[CTRY_GENITIVE])
    if actor == host and action == 1: toReturn = toReturn.replace("%", victimStr[new])
    else: toReturn = toReturn.replace("%", victimStr[7 if host.insgWing >= 0 else 6])
    return toReturn

def _generateTextStr(startingAt, howManyStrings):
    global strings
    toReturn = ""
    for i in range(startingAt, startingAt + howManyStrings):
        toReturn += random.choice(strings[CRISIS_STR][i].split("*"))
    return toReturn

def generateReactionLine(who, level, isMinor, isBDown):
    toReturn = ""
    # major crisis
    if not isMinor: 
        toReturn += _generateTextStr(who.id, 1)
        group = 2 if not isBDown else 3
    # minor crisis
    else: 
        if who.id > 2: group = 4 if not isBDown else 5
        else:
            return _generateTextStr(64 + who.id, 1) + _generateTextStr(66, 3)
    toReturn += _generateTextStr(_startingAt[group][level], _howManyStrings[group][level])
    return toReturn

def generateFirstHead(c):
    x,j = c.strengthRatio, 0
    while x > 1: x,j = x//2, j+1
    if j > 12: j = 12
    rank = (12-j) % 4
    i = (12 - j) // 4
    if j == 0: rank = 7 - 4 * c.strengthRatio
    i = 86 + (16 * i) + (4 * (3 & (c.random >> 8)))
    return getNewsHeadline(c, c, c, 5, i, rank)
    #return (i,rank)

def generateLastHead(c):
    if c.random > 0: i, x = 166, 13 * c.govtPopul
    else: i,x = 150, c.govtWing + 127
    if x > 255: x = 255
    i += ((x // 64) * 4)
    rank = (x % 64) // 16
    return getNewsHeadline(c, c, c, 5, i, rank)

def parseValue(mode, value):
    """
    Format a value for a given mode.

    """
    if mode in _modeUnits: g = _modeUnits[mode]
    elif 0 <= mode <= 5:
        return strings[TAG_POLICY][mode * 6 + value]
    elif mode == 8:
        return strings[TAG_RELATION][getMaxLevel((-100,-72,-44,-16,16,44,62,100), value)]
    if mode == 15: value += 2
    return strings[g][value]

def format(value):
    """
    Add thousands comma separator fot the given value.

    """
    return '{:,}'.format(value)

def formatValue(value, mode):
    # Military intervene
    if mode in (4,5): return format(value * 1000) + strings[UNIT][3]
    # Military aid
    elif mode in (2,3): return "$" + format(value * 10) + strings[UNIT][1]
    # Economic aid
    elif mode in (1,6): return "$" + format(value * 100) + strings[UNIT][1]
    # Population
    elif mode == 10: return format(value * 100000)
    # GNP
    elif mode == 11: return "$" + format(value * 100) + strings[UNIT][1]
    # GNP per capita
    elif mode == 12: return "$" + format(value)