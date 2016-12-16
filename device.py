# -*- coding: utf-8 -*-
import datetime
import threading
import time
import urllib.parse
import sys

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

        year, month, day = self._init_birth(18, 100)

        self._parameters = {
            'id': self._id,  # constant
            'timestamp': time.time(),
            'blood_pressure': {
                'systolic': None,
                'diastolic': None,
            },
            'pulse': None,
            'saturation': None,
            'electrodermal_response': None,
            'body_temperature': None,
            'blood_glucose_content': None,
            'blood_alcohol_content': None,
            'cholesterol': {
                'ldl': None,
                'hdl': None,
            },
            'steps': None,
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
        print(self._id)
        # return requests.post(self._url, json=self._parameters)


    @staticmethod
    def _init_birth(min_age=18, max_age=100):
        """ Generate random birth date """
        age = int((max_age - min_age) * numpy.random.beta(2, 4) + min_age)

        year = datetime.date.today().year - age
        month = 1 + numpy.random.randint(12)
        day = 1 + numpy.random.randint(28)

        return year, month, day
