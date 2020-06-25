from math import sqrt
from constants import *

def econConv(val):
    return (0,1,2,5,10,20)[val]

def mAidConv(val):
    return (0,1,5,20,50,100)[val]

def intvConv(val):
    return (0,1,5,20,100,500)[val]

def getMaxLevel(tresholds, x, **kwargs):
    t = 0
    if "lt" in kwargs and kwargs["lt"]:
        for i in range(len(tresholds)):
            if x < tresholds[i]: t += 1
    else:
        for i in range(len(tresholds)):
            if x > tresholds[i]: t += 1
    return t 

def milMax(x):
    """Maximum level of military aid for the government"""
    return getMaxLevel((-40,-20,0,20,40), x)

def intvGovtMax(level, x, dipl):
    """Maximum level of intervention for the government"""
    # For Advanced or Multipolar level maximum level is determined
    # by the type of treaty signed with the target
    if level >= 3:
        if x == 3: return 2
        elif x == 4: return 4
        elif x == 5: return 5
        else: return 0
    # On the easier levels, return the value based on the diplomatic opinion
    else:
        return getMaxLevel((0,20,40,60,80), dipl)

def intvInsgMax(world, superpower, country):
    """Maximum level of insurgency intervention"""
    y = 2
    # If superpower and country are contiguous - always maximum level
    if superpower.contig[country.id]: return 5
    # If not - the maximum level depends on the troops relocated
    # in the neighboring countries
    for k in world.country[2:]:
        if k.contig[country.id]:
            x = superpower.govtIntv[country.id]
            if x < 5: x += 1
            if x > y: y = x
    return y

def treatyMax(level, x):
    """Maximum level of treaty"""
    if level < 3: return 5
    return getMaxLevel((-60,0,40,60,100), x)

def econAidMax(x):
    """Maximum level of economic aid"""
    return getMaxLevel((-60,-40,-20,0,20), x)

def govtAidMax(x):
    """Maximum level of government military aid"""
    return getMaxLevel((-40,-20,0,20,40), x)

def insgAidMax(world, superpower, minorpower):
    """Maximum level of insurgency aid"""
    max = 1
    # If superpower and country are contiguous - always maximum level
    if superpower.contig[minorpower.id]: return 5
    # If not - the maximum level depends on the troops relocated
    # in the neighboring countries
    for k in world.country[2:]:
        if k.contig[minorpower.id]:
            x = superpower.govtIntv[k.id]
            if x < 5: x += 1
            if x > max: max = x
    return max

def maxPolicy(giver):
    maxPolicies = [5, 5]
    sumIntv = giver.totalIntv
    sumAid = giver.totalGovtAid
    men = giver.milMen
    spnd = giver.gnpSpnd[2]
    for i in range(4, -1, -1):
        if mAidConv(i + 1) > ((spnd // 8) + sumAid): maxPolicies[1] = i
        if intvConv(i + 1) > ((men // 4) - sumIntv): maxPolicies[0] = i
    return maxPolicies

def should(treaty):
    """How much obligation the given level of treaty creates"""
    return (0, 16, 32, 64, 96, 128)[treaty]

def changeDiplOpinion(i, j, delta):
    """Change diplomatic opinion between i and j by delta"""
    x = i.diplOpinion[j.id] + delta
    if x > 127: x = 127
    if x < -127: x = -127
    i.diplOpinion[j.id] = j.diplOpinion[i.id] = x

def changeDMess(world, c, howMuch):
    """Change sphere of influence of c by howMuch"""
    c.dMess += howMuch
    world.sumDMess += howMuch
    if world.sumDMess < 1: world.sumDMess = 1
    world.avdDMess = world.sumDMess / len(world.country)

def influence(s, c):
    """Get influence paramter of the superpower 's' over country 'c'"""
    x = s.treaty[c.id]\
        + s.econAid[c.id]\
        + s.govtAid[c.id]\
        + 2 * s.govtIntv[c.id]\
        - 2 * s.destab[c.id]\
        - 2 * s.insgAid[c.id]\
        - 4 * s.insgIntv[c.id]
    return (0 if x < 0 else x)

def hurt(target, action, old, new):
    x = 0
    if action == DESTAB:
        x = 16 * (new - old)
    elif action == ECONAID:
        x = -((1024 * (econConv(new) - econConv(old))) // target.GNP) // (target.govtPopul + 1)
    elif action == GOVTAID:
        x = ((old - new) * target.milPressure) // 4
    elif action == INSGAID:
        x = 12 * (new - old)
    elif action == GOVTINTV:
        x = ((old - new ) * target.milPressure) // 2
    elif action == INGSINTV:
        x = 25 * (new - old)
    elif action == PRESSURE:
        x = 8 * new
    elif action == TREATY:
        x = ((old - new) * target.milPressure) // 4
    if action in (1,2,4,7) and x == 0: x = old - new
    if x > 127: x = 127
    if x < -127: x = -127
    return x

def impt(toWhom, target, action, old, new):
    """Get importance for 'toWhom' for the given international policy change"""
    return (hurt(target, action, old, new) * toWhom.diplOpinion[target.id]) // 128

def gimpt(world, actor, action, target, old, new, bias):
    maxLongVal = 134144000
    for s in world.country[:2]:
        x = s.diplOpinion[target.id] // 4
        if x == 0: x = 1
        y = (should(s.treaty[target.id]) // 4) + 1
        z = (target.dMess * 1280) // world.sumDMess
        if z > 32: z = 32
        if z < 1: z = 1
        if s.id == 1: z = 33 - z
        t = s.adventurousness // 2
        if t > 32: t = 32
        if t < 1: t = 1
        v = hurt(target, action, old, new)
        if ((actor.id == 1 - s.id) and action in (2, 4, 7) and s.diplOpinion[target.id] > 0):
            v = -v
        if bias == 1:
            x, y = x * int(sqrt(abs(x))), int(sqrt(y))
        elif bias == 2:
            y, z = y * int(sqrt(y)), int(sqrt(z))
        elif bias == 3:
            z, t = z * int(sqrt(z)), int(sqrt(t))
        elif bias == 4:
            t *= int(sqrt(t))
            x = int(sqrt(x)) if x > 0 else - int(sqrt(abs(x)))
        lx = ((z * x * y * t * v) // 64) * target.prestigeVal
        if s.id == 0: ly = lx
        else: lz = lx
        if lx > maxLongVal: lx = maxLongVal
        if lx < -maxLongVal: lx = -maxLongVal
        lx //= 4096
        if s.id == 0: world.crisis.usaImpt = lx
        else: world.crisis.ussrImpt = lx
    lx = ly + lz
    if lx > maxLongVal: lx = maxLongVal
    elif lx < -maxLongVal: lx = -maxLongVal
    return lx // 4096

def doPolicy(world, actor, target, action, new, **kwargs):
    """
    Enact a policy and calculate effects on available resources for the actor if applicable.
    This function does not calculate the effects of the given policy.

    """
    if actor.id < 2:
        policies = (actor.destab, actor.econAid, actor.govtAid,
            actor.insgAid, actor.govtIntv, actor.insgIntv, actor.pressure, actor.treaty)
    else: policies = (None, None, actor.govtAid, actor.insgAid, actor.govtIntv, actor.insgIntv,
        None, None)
    old = policies[action][target.id]
    policies[action][target.id] = new
    if action == 2:
        target.totalGovtAid = target.totalGovtAid - mAidConv(old) + mAidConv(new)
        actor.totalGovtAid = actor.totalGovtAid + mAidConv(old) - mAidConv(new)
    elif action == 3:
        actor.totalGovtAid = actor.totalGovtAid + mAidConv(old) - mAidConv(new)
    elif action in (4,5):
        actor.totalIntv = actor.totalIntv - intvConv(old) + intvConv(new)
    if old != new or actor.id == world.human:
        crisis = kwargs["crisis"] if "crisis" in kwargs else old > new
        world.addNews(actor, target, target, action, old, new, crisis)