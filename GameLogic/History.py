class History:

    # Static list of history entry attributes, their names should be identical
    # to attribute names inside Country or Superpower classes so that the update()
    # method can copy values easily using getattr() built-in method
    props = ("sqrtStrength", "GNP", "population", "milPressure", "govtPopul",
        "govtAid", "insgAid", "govtIntv", "insgIntv", "diplOpinion", "econAid", "destab",
        "pressure", "treaty", "gnpSpnd", "gnpFrac")

    def __init__(self, parent):
        super(History, self).__init__()
        self.c = parent
        self.sqrtStrength = [[]]
        self.GNP = [[]]
        self.GNPcap = [[]]
        self.population = [[]]
        self.milPressure = [[]]
        self.govtPopul = [[]]
        self.govtAid = [[],[]]
        self.insgAid = [[],[]]
        self.govtIntv = [[],[]]
        self.insgIntv = [[],[]]
        self.diplOpinion = [[],[]]
        self.econAid = [[],[]]
        self.destab = [[],[]]
        self.pressure = [[],[]]
        self.treaty = [[],[]]
        self.finlProb = [[],[]]
        self.gnpSpnd = [[],[],[]]
        self.gnpFrac = [[],[],[]]

    def update(self):
        for attrName in self.props:
            attr = getattr(self, attrName)
            # 1-dim list: copy attribute from parent country
            if len(attr) == 1: attr[0].append(getattr(self.c, attrName))
            # 2-dim list: international relationship towards the two superpowers
            # copy attribute from the Superpower object
            elif len(attr) == 2:
                for i in range(2): attr[i].append(getattr(self.c.parent.country[i], attrName)[self.c.id])
            # 3-dim list: GNP economy data, copy attribute from parent country
            elif len(attr) == 3:
                for i in range(3): attr[i].append(getattr(self.c, attrName)[i])
        # update GNP per capita
        self.GNPcap.append(self.c.getGNPpcap(3))
        # update finlandization probability
        for i in range(2): self.finlProb[i].append(self.c.finlProb[i])
