# -*- coding: utf-8 -*-
import atexit
import argparse

from device import Device


class Startup(object):
    """ Simulation startup """

    def __init__(self, address, port, n_devices=10):
        self._address = address
        self._port = port
        self._devices = [Device(device_id) for device_id in range(n_devices)]

    def start(self):
        for device in self._devices:
            device.bind_server(self._address, self._port)
            device.run()

    @atexit.register
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
                            default=10, help="number of devices to simulate")

        args = parser.parse_args(argv)

        return Startup(args.devices)


if __name__ == '__main__':
    startup = Startup.application()
