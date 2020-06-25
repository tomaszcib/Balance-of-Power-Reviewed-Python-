# map modes
M_SPHINFL = 0
M_EVENTS = 1
M_PRESTIGE = 2
M_INSG = 3
M_GOVTSTAB = 4
M_FINLPROB_USA = 5
M_FINLPROB_USSR = 6
M_WAR = 7
M_DIPL_OUT = 8
M_GOVTAID_OUT = 9
M_INSGAID_OUT = 10
M_GOVTINTV_OUT = 11
M_INSGINTV_OUT = 12
M_ECONAID = 13
M_DESTAB = 14
M_PRESS = 15
M_TREATY = 16
M_DIPL_IN = 17
M_GOVTAID_IN = 18
M_INSGAID_IN = 19
M_GOVTINTV_IN = 20
M_INSGINTV_IN = 21
M_GNP = 22
M_GNPCAP = 23
M_POP = 33
M_MILMEN = 34

# policies
DESTAB = 0
ECONAID = 1
GOVTAID = 2
INSGAID = 3
GOVTINTV = 4
INGSINTV = 5
PRESSURE = 6
TREATY = 7
AVL_ACTIONS = ((2,3,4,5), (0,1,2,3,4,5), range(8), range(8))
INAVL_MAP_MODES = ((4,5,6,7,13,14,15,16),
                 (5,6,7,15,16), (7,), tuple())
CLOSE_UP_AVL_DATA = (range(6), range(8), range(12), range(12))
CLOSE_UP_SUPERPWR = (range(2,6,1), range(2,7,1), range(2,7,1), range(2,7,1))

# units
ENCYCLOPEDIA_UNITS = (4,6,10,7,4,4,8,8,11,11,11,11,
    11,11,9,9,5,5,5,5,5,5,5)

# default options
DEFAULT_OPTS = (True, True, False, "english.json", 0, 0, 0)