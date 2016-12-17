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

    URL_SCHEME = 'http'
    URL_PATH = '/api/device/send'
    URL_PARAMS = ''
    URL_QUERY = ''
    URL_FRAGMENT = ''

    _PRINT_LOCK = threading.Lock()

    GPS_R = 6478137  # earth's radius in meters


    def __init__(self, device_id, delay=1):
        """ Initialize parameters """
        threading.Thread.__init__(self)

        self._id = device_id
        self._delay = delay

        self._stop_event = threading.Event()
        self._ready_event = threading.Event()

        self._url = None
        self._session = requests.Session

        year, month, day = self._init_birth(Limits.AGE.min, Limits.AGE.max)

        systolic = self._init_systolic_pressure(130)
        diastolic = self._init_diastolic_pressure(77)

        ldl = self._init_cholesterol_ldl(90, 200)
        hdl = self._init_cholesterol_hdl(30, 70)

        steps = self._steps(delay)

        pulse = self._init_pulse(60,100)

        saturation = self._init_saturation(0,100)

        body_temperature = self._init_body_temperature(36.5,37.5)

        electrodermal_response = self._init_electrodermal_response(0.3,0.37)

        blood_alcohol_content = self._init_blood_alcohol_content(0, 0.5)

        blood_glucose_content = self._init_blood_glucose_content(50,380)

        lat, lon = self._init_gps(Limits.GPS_LATITUDE, Limits.GPS_LONGITUDE)

        self._parameters = {
            'id': self._id,  # constant
            'timestamp': time.time(),
            'blood_pressure': {
                'systolic': systolic,
                'diastolic': diastolic,
            },
            'pulse': pulse,
            'saturation': saturation,
            'electrodermal_response': electrodermal_response,
            'body_temperature': body_temperature,
            'blood_glucose_content': blood_glucose_content,
            'blood_alcohol_content': blood_alcohol_content,
            'cholesterol': {
                'ldl': ldl,
                'hdl': hdl,
            },
            'steps': steps,
            'gps': {
                'latitude': lat,
                'longitude': lon,
            },
            'birth': {
                'year': year,
                'month': month,
                'day': day,
            }
        }


    def bind_server(self, address, port):
        """ Bind target server to the device """
        components = (self.URL_SCHEME,
                      ':'.join([address, str(port)]),
                      self.URL_PATH,
                      self.URL_PARAMS,
                      self.URL_QUERY,
                      self.URL_FRAGMENT)

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

        old_timestamp = self._parameters['timestamp']

        self._parameters['timestamp'] = time.time()

        delta_time = self._parameters['timestamp'] - old_timestamp

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


    @staticmethod
    def _init_birth(min_age=18, max_age=100):
        """ Generate random birth date """
        age = int((max_age - min_age) * numpy.random.beta(2, 4) + min_age)

        year = datetime.date.today().year - age
        month = 1 + numpy.random.randint(12)
        day = 1 + numpy.random.randint(28)

        return year, month, day


    @staticmethod
    def _init_systolic_pressure(avg=130):
        """ Generate initial systolic blood pressure """
        # good ~130
        return round(scipy.stats.norm.rvs(avg, 20), 1)


    @staticmethod
    def _init_diastolic_pressure(avg=77):
        """ Generate initial diastolic blood pressure """
        # good ~77
        return round(scipy.stats.norm.rvs(avg, 13), 1)


    @staticmethod
    def _init_cholesterol_ldl(m=90, M=200):
        """ Generate initial LDL cholesterol """
        # best=90, worst=200
        return round(scipy.stats.beta.rvs(0.3, 3, m, M - m), 2)


    @staticmethod
    def _init_cholesterol_hdl(m=30, M=70):
        """ Generate initial HDL cholesterol """
        # best=70, worst=30
        return round(scipy.stats.beta.rvs(2, 0.1, m, M - m), 2)


    @staticmethod
    def _steps(delay):
        """ Generate steps """
        # average 1 step per second
        return round(numpy.random.uniform(0, delay), 0)


    @staticmethod
    def _init_pulse(m=60, M=100):
        """ Generate initial pulse """
        # mingood = 60 max good=100, other values are bad
        return round(scipy.stats.norm.rvs((M + m) / 2, 12), 1)


    @staticmethod
    def _init_saturation(m=0, M=100):
        """ Generate initial saturation """
        # 0=RIP, <55% - loss of consciousness, 55-65 - impaired mental function,
        # 90+ normal
        return round(scipy.stats.beta.rvs(15, 0.5, m, M - m), 2)


    @staticmethod
    def _init_body_temperature(m=36.5, M=37.5):
        """ Generate initial body temperature """
        # normal 36.5-37.5
        return round(scipy.stats.norm.rvs((M + m) / 2, 0.7), 2)


    @staticmethod
    def _init_electrodermal_response(m=0.3, M=0.37):
        """ Generate initial electrodermal response """
        # should be between 0.3-0.37
        return round(scipy.stats.norm.rvs((M + m) / 2, 0.01), 4)


    @staticmethod
    def _init_blood_alcohol_content(m=0, M=0.5):
        """ Generate initial blood alcohol content """
        # normal=0, 0.5 alcohol poisoning
        return round(scipy.stats.beta.rvs(0.05, 2, m, M - m), 3)


    @staticmethod
    def _init_blood_glucose_content(m=50, M=380):
        """ Generate initial blood glucose content """
        # 215+ action sugessted
        return round(scipy.stats.beta.rvs(0.05, 2, m, M - m), 1)

    @staticmethod
    def _init_gps(limit_lat, limit_lon):
        """ Generate initial GPS position """
        lat = round(numpy.random.uniform(limit_lat.min, limit_lat.max), 8)
        lon = round(numpy.random.uniform(limit_lon.min, limit_lon.max), 8)
        return lat, lon

    def _gps_add_meters(lat, lon, d_north, d_east):
        """ Add specified amount of meters to GPS position """
        d_lat = distance_north / self.GPS_R
        d_lon = distance_east / (self.GPS_R * numpy.cos(lat * numpy.pi / 180))

        n_lat = lat + d_lat * 180 / numpy.pi
        n_lon = lon + d_lon * 180 / numpy.pi

        n_lat = round((n_lat + 90) % 180 - 90, 8)    # -90 to 90
        n_lon = round((n_lon + 180) % 360 - 180, 8)  # -180 to 180

        return n_lat, n_lon

    def __str__(self):
        return 'Device(id=%s, parameters=%s)' % (
            str(self._id),
            str(self._parameters)
        )
