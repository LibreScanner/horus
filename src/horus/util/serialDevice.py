'''
Copyright 2014 Christian Fobel
Copyright 2011 Ryan Fobel

This file is part of serial_device.

serial_device is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

serial_device is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with serial_device.  If not, see <http://www.gnu.org/licenses/>.
'''

##                    ##
##-- TODO: refactor --##
##                    ##

import os
import itertools
from time import sleep

from pathHelpers import path


def get_serial_ports():
    if os.name == 'nt':
        ports = _get_serial_ports_windows()
    else:
        ports = itertools.chain(path('/dev').walk('ttyUSB*'),
                                path('/dev').walk('ttyACM*'))
    # sort list alphabetically
    ports_ = [port for port in ports]
    ports_.sort()
    for port in ports_:
        yield port


def _get_serial_ports_windows():
    '''
    Uses the Win32 registry to return a iterator of serial (COM) ports existing
    on this computer.

    See http://stackoverflow.com/questions/1205383/listing-serial-com-ports-on-windows
    '''
    import _winreg as winreg

    reg_path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
    except WindowsError:
        # No serial ports. Return empty generator.
        return

    for i in itertools.count():
        try:
            val = winreg.EnumValue(key, i)
            yield str(val[1])
        except EnvironmentError:
            break


class ConnectionError(Exception):
    pass


class SerialDevice(object):
    '''
    This class provides a base interface for encapsulating interaction with a
    device connected through a serial-port.

    It provides methods to automatically resolve a port based on an
    implementation-defined connection-test, which is applied to all available
    serial-ports until a successful connection is made.

    Notes
    =====

    This class intends to be cross-platform and has been verified to work on
    Windows and Ubuntu.
    '''
    def __init__(self):
        self.port = None

    def get_port(self, baud_rate):
        '''
        Using the specified baud-rate, attempt to connect to each available
        serial port.  If the `test_connection()` method returns `True` for a
        port, update the `port` attribute and return the port.

        In the case where the `test_connection()` does not return `True` for
        any of the evaluated ports, raise a `ConnectionError`.
        '''
        self.port = None

        for test_port in get_serial_ports():
            if self.test_connection(test_port, baud_rate):
                self.port = test_port
                break
            sleep(0.1)

        if self.port is None:
            raise ConnectionError('Could not connect to serial device.')

        return self.port

    def test_connection(self, port, baud_rate):
        '''
        Test connection to device using the specified port and baud-rate.

        If the connection is successful, return `True`.
        Otherwise, return `False`.
        '''
        raise NotImplementedError