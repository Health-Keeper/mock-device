# -*- coding: utf-8 -*-
import collections


# A named tuple of values for simple limit handling
Limit = collections.namedtuple('Limit', ['min', 'max'])


class Limits(object):
    """ Value limits for device parameters """
    AGE = Limit(18, 100)
    BLOOD_PRESSURE_SYSTOLIC = Limit(None, None)
    BLOOD_PRESSURE_DIASTOLIC = Limit(None, None)
    PULSE = Limit(None, None)
    SATURATION = Limit(None, None)
    ELECTRODERMAL_RESPONSE = Limit(None, None)
    BODY_TEMPERATURE = Limit(None, None)
    BLOOD_BLUCOSE_CONTENT = Limit(None, None)
    BLOOD_ALCOHOL_CONTENT = Limit(0, None)
    CHOLESTEROL_LDL = Limit(None, None)
    CHOLESTEROL_HDL = Limit(None, None)
    GPS_LATITUDE = Limit(None, None)
    GPS_LONGITUDE = Limit(None, None)
