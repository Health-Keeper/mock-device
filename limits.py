# -*- coding: utf-8 -*-
import collections


# A named tuple for simple limit handling
# minimum maximum average decimals
Limit = collections.namedtuple('Limit', ['min', 'max', 'avg', 'd'])


class Limits(object):
    """ Value limits for device parameters """
    AGE = Limit(18, 100, None, 0)
    BPS = Limit(None, None, 130, 1)
    BPD = Limit(None, None, 77, 1)
    PUL = Limit(60, 100, None, 1)
    SAT = Limit(0, 100, None, 2)
    EDR = Limit(0.3, 0.37, None, 4)
    BTP = Limit(36.5, 37.5, None, 2)
    BGC = Limit(50, 380, None, 1)
    BAC = Limit(0, 0.05, None, 3)
    LDL = Limit(90, 200, None, 2)
    HDL = Limit(30, 70, None, 2)
    LAT = Limit(-90, 90, None, 8)
    LON = Limit(-180, 180, None, 8)
