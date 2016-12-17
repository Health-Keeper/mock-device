# -*- coding: utf-8 -*-
import datetime
import sys
import threading
import time
import urllib.parse

import numpy
import requests
import scipy.stats

from limits import Limits


class Device(threading.Thread):
    """ Mocked IoT device """

    _URL_SCHEME = 'http'
    _URL_PATH = '/api/device/send'
    _URL_PARAMS = ''
    _URL_QUERY = ''
    _URL_FRAGMENT = ''

    _PRINT_LOCK = threading.Lock()

    _MONTH = {
        1: 31,
        2: 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }

    _GPS_R = 6478137  # earth's radius in meters


    def __init__(self, device_id, delay=1):
        """ Initialize parameters """
        threading.Thread.__init__(self)

        self._id = device_id
        self._delay = delay

        self._stop_event = threading.Event()
        self._ready_event = threading.Event()

        self._url = None
        self._session = requests.Session

        self._bps = self._init_bps(Limits.BPS.avg)
        self._bpd = self._init_bpd(Limits.BPD.avg)
        self._pul = self._init_pul(Limits.PUL.min, Limits.PUL.max)
        self._sat = self._init_sat(Limits.SAT.min, Limits.SAT.max)
        self._edr = self._init_edr(Limits.EDR.avg)
        self._btp = self._init_btp(Limits.BTP.avg)
        self._bgc = self._init_bgc(Limits.BGC.min, Limits.BGC.max)
        self._bac = self._init_bac(Limits.BAC.min, Limits.BAC.max)
        self._ldl = self._init_ldl(Limits.LDL.min, Limits.LDL.max)
        self._hdl = self._init_hdl(Limits.HDL.min, Limits.HDL.max)
        self._gps = self._init_gps(Limits.LAT, Limits.LON)
        self._birth = self._init_birth(Limits.AGE.min, Limits.AGE.max)

        lat, lon = self._gps
        y, m, d = self._birth

        self._parameters = {
            'id': self._id,  # constant
            'timestamp': time.time(),
            'blood_pressure': {
                'systolic': self._bps,
                'diastolic': self._bpd,
            },
            'pulse': self._pul,
            'saturation': self._sat,
            'electrodermal_response': self._edr,
            'body_temperature': self._btp,
            'blood_glucose_content': self._bgc,
            'blood_alcohol_content': self._bac,
            'cholesterol': {
                'ldl': self._ldl,
                'hdl': self._hdl,
            },
            'steps': self._steps(self._delay),
            'gps': {
                'latitude': lat,
                'longitude': lon,
            },
            'birth': {
                'year': y,
                'month': m,
                'day': d,
            }
        }


    def bind_server(self, address, port):
        """ Bind target server to the device """
        components = (self._URL_SCHEME,
                      ':'.join([address, str(port)]),
                      self._URL_PATH,
                      self._URL_PARAMS,
                      self._URL_QUERY,
                      self._URL_FRAGMENT)

        self._url = urllib.parse.urlunparse(components)


    def run(self):
        """ Run device thread """
        while self.is_running():
            try:
                self._stop_event.wait(self._delay)
                self._update()
                self._send()
            except Exception as e:
                with self._PRINT_LOCK:
                    print(e, file=sys.stderr)

    def stop(self):
        """ Stop device thread execution """
        self._stop_event.set()


    def is_running(self):
        """ Determine if device thread is running """
        return not self._stop_event.is_set()


    def ready(self):
        """ Mark device as ready to operate """
        self._ready_event.set()


    def is_ready(self):
        """ Check if device is ready for processing """
        return self._ready_event.is_set()


    def _update(self):
        """ Update values of the parameters """
        if not self.is_ready():
            return

        self._parameters['timestamp'] = time.time()
        self._parameters['steps'] = self._steps(self._delay)


    def _send(self):
        """ Send device parameters to target server """
        if not self.is_ready():
            return

        if self._url is None:
            raise ConnectionError(("No target server bound for device ID "
                                   "'%s'.") % self._id)

        # Disabled until target server is not online
        # return self._session.post(self._url, json=self._parameters)


    def _init_birth(self, m=18, M=100):
        """ Generate random birth date """
        age = int((M - m) * numpy.random.beta(2, 4) + m)

        year = datetime.date.today().year - age
        month = 1 + numpy.random.randint(12)
        day = 1 + numpy.random.randint(self._MONTH[month])

        return year, month, day


    @staticmethod
    def _init_bps(avg=130):
        """ Generate initial systolic blood pressure """
        # good ~130
        return round(scipy.stats.norm.rvs(avg, 20), Limits.BPS.d)


    @staticmethod
    def _init_bpd(avg=75):
        """ Generate initial diastolic blood pressure """
        # good ~77
        return round(scipy.stats.norm.rvs(avg, 13), Limits.BPD.d)


    @staticmethod
    def _init_ldl(m=90, M=200):
        """ Generate initial LDL cholesterol """
        # best=90, worst=200
        return round(scipy.stats.beta.rvs(0.3, 3, m, M - m), Limits.LDL.d)


    @staticmethod
    def _init_hdl(m=30, M=70):
        """ Generate initial HDL cholesterol """
        # best=70, worst=30
        return round(scipy.stats.beta.rvs(2, 0.1, m, M - m), Limits.HDL.d)


    @staticmethod
    def _steps(delay):
        """ Generate steps """
        # average 1 step per second
        return round(numpy.random.uniform(0, delay), 0)


    @staticmethod
    def _init_pul(m=60, M=100):
        """ Generate initial pulse """
        # mingood = 60 max good=100, other values are bad
        return round(scipy.stats.norm.rvs((M + m) / 2, 12), Limits.PUL.d)


    @staticmethod
    def _init_sat(m=0, M=100):
        """ Generate initial saturation """
        # 0=RIP, <55% - loss of consciousness, 55-65 - impaired mental function,
        # 90+ normal
        return round(scipy.stats.beta.rvs(15, 0.5, m, M - m), Limits.SAT.d)


    @staticmethod
    def _init_btp(avg=37):
        """ Generate initial body temperature """
        # normal 36.5-37.5
        return round(scipy.stats.norm.rvs(avg, 0.7), Limits.BTP.d)


    @staticmethod
    def _init_edr(avg=0.325):
        """ Generate initial electrodermal response """
        # should be between 0.3-0.37
        return round(scipy.stats.norm.rvs(avg, 0.02), Limits.EDR.d)


    @staticmethod
    def _init_bac(m=0, M=0.5):
        """ Generate initial blood alcohol content """
        # normal=0, 0.5 alcohol poisoning
        return round(scipy.stats.beta.rvs(0.05, 2, m, M - m), Limits.BAC.d)


    @staticmethod
    def _init_bgc(m=50, M=380):
        """ Generate initial blood glucose content """
        # 215+ action sugessted
        return round(scipy.stats.beta.rvs(0.05, 2, m, M - m), Limits.BGC.d)

    @staticmethod
    def _init_gps(limit_lat, limit_lon):
        """ Generate initial GPS position """
        lat = round(numpy.random.uniform(limit_lat.min, limit_lat.max),
                    Limits.LAT.d)
        lon = round(numpy.random.uniform(limit_lon.min, limit_lon.max),
                    Limits.LON.d)
        return lat, lon

    def _gps_add_meters(self, lat, lon, d_north, d_east):
        """ Add specified amount of meters to GPS position """
        d_lat = d_north / self._GPS_R
        d_lon = d_east / (self._GPS_R * numpy.cos(lat * numpy.pi / 180))

        n_lat = lat + d_lat * 180 / numpy.pi
        n_lon = lon + d_lon * 180 / numpy.pi

        n_lat = round((n_lat + 90) % 180 - 90, Limits.LAT.d)
        n_lon = round((n_lon + 180) % 360 - 180, Limits.LON.d)

        return n_lat, n_lon

    def __str__(self):
        return 'Device(id=%s, parameters=%s)' % (
            str(self._id),
            str(self._parameters)
        )
