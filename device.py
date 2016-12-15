# -*- coding: utf-8 -*-
import threading
import time
import urllib.parse

import requests


class Device(threading.Thread):
    """ Mocked IoT device """

    URL_SCHEME = 'http'
    URL_PATH = '/api/device/send'
    URL_PARAMS = ''
    URL_QUERY = ''
    URL_FRAGMENT = ''

    def __init__(self, device_id, delay=10, stop_event=None):
        """ Initialize parameters """
        super()

        self._id = device_id
        self._delay = delay

        self._stop_event = stop_event or threading.Event()

        self._url = None

        self._parameters = {
            'id': self._id,  # constant
            'timestamp': time.time()
            'blood_pressure': {
                'systolic': None,
                'diastolic': None
            }
            'pulse': None,
            'saturation': None,
            'electrodermal_response': None,
            'body_temperature': None,
            'blood_glucose_content': None,
            'blood_alcohol_content': None,
            'cholesterol': {
                'ldl': None,
                'hdl': None
            },
            'steps': None,
            'gps': {
                'latitude': None,
                'longitude': None
            },
            'birth': {
                'year': None,
                'month': None,
                'day': None
            }
        }

    def bind_server(self, address, port):
        """ Bind target server to the device """
        components = (self.URL_SCHEME,
                      ':'.join(address, port),
                      self.URL_PATH,
                      self.URL_PARAMS,
                      self.URL_QUERY,
                      self.URL_FRAGMENT)

        self._url = urllib.parse.urlunparse(components)

    def run(self):
        """ Run device thread """
        while self.is_running():
            self._stop_event.wait(self._delay)
            self._update()
            self._send()

    def stop(self):
        """ Stop device thread execution """
        self._stop_event.set()

    def is_running(self):
        """ Determine if device thread is running """
        return not self._stop_event.is_set()

    def _update(self):
        """ Update values of the parameters """
        old_timestamp = self._parameters['timestamp']
        self._parameters['timestamp'] = time.time()
        delta_time = self._parameters['timestamp'] - old_timestamp

    def _send(self):
        """ Send device parameters to target server """
        if self._url is None:
            raise ConnectionError(("No target server bound for device ID "
                                   "'%s'.") % self._id)

        return requests.post(self._url, json=self._parameters)
