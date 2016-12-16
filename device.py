# -*- coding: utf-8 -*-
import datetime
import threading
import time
import urllib.parse
import sys

from scipy.stats import norm
from scipy.stats import beta
from random import randint

import numpy
import requests


class Device(threading.Thread):
    """ Mocked IoT device """

    URL_SCHEME = 'http'
    URL_PATH = '/api/device/send'
    URL_PARAMS = ''
    URL_QUERY = ''
    URL_FRAGMENT = ''

    _PRINT_LOCK = threading.Lock()


    def __init__(self, device_id, delay=1):
        """ Initialize parameters """
        threading.Thread.__init__(self)

        self._id = device_id
        self._delay = delay

        self._stop_event = threading.Event()
        self._ready_event = threading.Event()

        self._url = None
        self._session = requests.Session

        year, month, day = self._init_birth(18, 100)
        systolic = self._init_systolic_pressure(130)
        diastolic = self._init_diastolic_pressure(77)
        ldl = self._init_cholesterol_ldl(90, 200)
        hdl = self._init_cholesterol_hdl(30, 70)
        steps = self._init_steps(delay)
        pulse = self._init_pulse(60,100)
        saturation = self._init_saturation(0,100)
        body_temperature = self._init_body_temperature(36.5,37.5)
        electrodermal_response = self._init_electrodermal_response(0.3,0.37)
        blood_alcohol_content = self._init_blood_alcohol_content(0, 0.5)
        blood_glucose_content = self._init_blood_glucose_content(50,380)

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
                'latitude': None,
                'longitude': None,
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
        return self._ready_event.is_set()


    def _update(self):
        """ Update values of the parameters """
        if not self.is_ready():
            return

        old_timestamp = self._parameters['timestamp']

        self._parameters['timestamp'] = time.time()

        delta_time = self._parameters['timestamp'] - old_timestamp


    def _send(self):
        """ Send device parameters to target server """
        if not self.is_ready():
            return

        if self._url is None:
            raise ConnectionError(("No target server bound for device ID "
                                   "'%s'.") % self._id)

        # Testing
        with self._PRINT_LOCK:
            print(self._id)
            
        # return self._session.post(self._url, json=self._parameters)


    @staticmethod
    def _init_birth(min_age=18, max_age=100):
        """ Generate random birth date """
        age = int((max_age - min_age) * numpy.random.beta(2, 4) + min_age)

        year = datetime.date.today().year - age
        month = 1 + numpy.random.randint(12)
        day = 1 + numpy.random.randint(28)

        return year, month, day

    #good ~130
    @staticmethod
    def _init_systolic_pressure(avg=130):
        systolic = norm.rvs(loc=avg, scale=20, size=1, random_state=None)

        return systolic

    #good ~77
    @staticmethod
    def _init_diastolic_pressure(avg=77):
        diastolic = norm.rvs(loc=avg, scale=13, size=1, random_state=None)

        return diastolic

    #best=90, worst=200
    @staticmethod
    def _init_cholesterol_ldl(minimum=90, maximum=200):
        return beta.rvs(a=0.3, b=3, loc=minimum, scale=maximum-minimum, size=1, random_state=None)

    #best=70, worst=30
    @staticmethod
    def _init_cholesterol_hdl(minimum=30, maximum=70):
        return beta.rvs(a=2, b=0.1,  loc=minimum, scale=maximum-minimum, size=1, random_state=None)

    #average 1 step per second
    @staticmethod
    def _init_steps(delay):
        return randint(0,(int)(delay/1000))

    #mingood = 60 max good=100, other values are bad
    @staticmethod
    def _init_pulse(minimum=60, maximum=100):
        return norm.rvs(loc=(maximum+minimum)/2, scale=12, size=1, random_state=None)

    #0=RIP, <55% - loss of consciousness, 55-65 - impaired mental function, 90+ normal
    @staticmethod
    def _init_saturation(minimum=0, maximum=100):
        return beta.rvs(a=15, b=0.5, loc=minimum, scale=maximum-minimum, size=1, random_state=None)

    #normal 36.5-37.5
    @staticmethod
    def _init_body_temperature(minimum=36.5, maximum= 37.5):
        return norm.rvs(loc=(maximum+minimum)/2, scale=0.7, size=1, random_state=None)

    #should be between 0.3-0.37
    @staticmethod
    def _init_electrodermal_response(minimum=0.3, maximum=0.37):
        return norm.rvs(loc=(minimum+maximum)/2, scale=0.01, size=1, random_state=None)

    #normal=0, 0.5 alcohol poisoning
    @staticmethod
    def _init_blood_alcohol_content(minimum=0, maximum=0.5):
        return beta.rvs(a=0.05, b=2, loc=minimum, scale=maximum-minimum, size=1, random_state=None)

    #215+ action sugessted
    @staticmethod
    def _init_blood_glucose_content(minimum=50, maximum=380):
        return beta.rvs(a=0.05, b=2, loc=minimum, scale=maximum - minimum, size=1, random_state=None)