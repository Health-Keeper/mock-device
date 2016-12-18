# -*- coding: utf-8 -*-
import collections


# A named tuple for simple limit handling
# minimum maximum average decimals
Limit = collections.namedtuple('Limit', ['min', 'max', 'avg', 'd'])


class Limits(object):
    """ Value limits for device parameters """
    BPS = Limit(40, 220, 130, 2)
    BPD = Limit(30, 120, 75, 2)
    PUL = Limit(60, 100, None, 1)
    SAT = Limit(0, 100, None, 2)
    EDR = Limit(0.2, 0.45, 0.325, 4)
    BTP = Limit(34, 40, 37, 2)
    BGC = Limit(50, 380, None, 1)
    BAC = Limit(0, 0.05, None, 3)
    LDL = Limit(90, 200, None, 2)
    HDL = Limit(30, 70, None, 2)
    LAT = Limit(-90, 90, None, 8)
    LON = Limit(-180, 180, None, 8)
