# -*- coding: utf-8 -*-
import atexit
import argparse
import time

import numpy
import progressbar

from device import Device


class Startup(object):
    """ Simulation startup """

    def __init__(self, address, port, n_devices=10):
        self._address = address
        self._port = port

        self._devices = [Device(device_id) for device_id in range(n_devices)]

        atexit.register(self.stop)

    def start(self):
        i = 0
        with progressbar.ProgressBar(max_value=len(self._devices), widgets=[
                " Starting devices: ", progressbar.Counter(), " ",
                progressbar.Bar(),
                " ", progressbar.Percentage(), " "
        ]) as bar:
            for device in self._devices:
                time.sleep(numpy.random.uniform())

                device.bind_server(self._address, self._port)
                device.start()

                bar.update(i)
                i += 1

        for device in self._devices:
            device.ready()

    def stop(self):
        for device in self._devices:
            if not device.is_running():
                continue
            device.stop()

    @staticmethod
    def application(argv=None):
        parser = argparse.ArgumentParser(prog=__file__,
                                         description="IoT device simulator")

        parser.add_argument('-n', '--devices', type=int, action='store',
                            default=10, metavar='N',
                            help="number of devices to simulate")

        parser.add_argument('-a', '--address', type=str, action='store',
                            default='localhost', metavar='ADDRESS',
                            help="API server address")

        parser.add_argument('-p', '--port', type=int, action='store',
                            default=80, metavar='PORT', help="API server port")

        args = parser.parse_args(argv)

        return Startup(args.address, args.port, args.devices)


if __name__ == '__main__':
    startup = Startup.application()

    startup.start()

    # Wait for user interruption
    input('Windows: Ctrl-Z+Enter')

    startup.stop()
