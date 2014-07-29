#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: July 2014                                                       #
# Author: Álvaro Velad Galván <alvaro.velad@bq.com>                     #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.  #
#                                                                       #
#-----------------------------------------------------------------------#

import os
from subprocess import Popen, PIPE, CalledProcessError
import logging
import platform
import resources

from pathHelpers import path
from serialDevice import SerialDevice, ConnectionError


logger = logging.getLogger()


class FirmwareError(Exception):
    pass


class AvrDude(SerialDevice):
    def __init__(self, protocol="arduino", microcontroller="atmega328p", baud_rate="115200", conf_path=None,
                 port=None):
        self.protocol = protocol
        self.microcontroller = microcontroller
        self.baud_rate = baud_rate

        if os.name == 'nt':
        	self.avrdude = path(resources.getPathForToolsWindows("avrdude.exe")).abspath()
        elif platform.architecture()[0] == '64bit':
            self.avrdude = path(resources.getPathForToolsLinux("avrdude-x64")).abspath()
        else:
            self.avrdude = path(resources.getPathForToolsLinux("avrdude")).abspath()
        print "avrdude path=%s" % self.avrdude
        logger.info("avrdude path=%s" % self.avrdude)
        if self.avrdude is None:
            raise FirmwareError('avrdude not installed')
        if conf_path is None:
            if os.name == 'nt':
                self.avrconf = path(resources.getPathForToolsWindows("avrdude.conf")).abspath()
            else:
                self.avrconf = path(resources.getPathForToolsLinux("avrdude-linux.conf")).abspath()
        else:
            self.avrconf = path(conf_path).abspath()
        if port:
            self.port = port
            print 'avrdude set to connect on port: %s' % self.port
            logger.info('avrdude set to connect on port: %s' % self.port)
        else:
            # No serial-port was specified.  Call `SerialDevice.get_port`
            # method to iterate through each available serial-port until a
            # connection is successfully made.
            self.port = self.get_port(baud_rate)
	    print 'avrdude successfully connected on port: %s' % self.port
            logger.info('avrdude successfully connected on port: %s' %
                        self.port)

    def _run_command(self, flags):
        config = dict(avrdude=self.avrdude, avrconf=self.avrconf)

        cmd = ['%(avrdude)s'] + flags
        cmd = [v % config for v in cmd]

        logger.info(' '.join(cmd))
        print ' '.join(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = p.communicate()
        if p.returncode:
            raise ConnectionError(stderr)
        return stdout, stderr

    def flash(self, hex_path=resources.getPathForFirmware("horus.hex"), extra_flags=None):
        hex_path = path(hex_path)
        print hex_path
        flags = ['-c', self.protocol, '-b', str(self.baud_rate), '-p',
                 self.microcontroller, '-P', '%s' % self.port, '-U',
                 'flash:w:%s:i' % hex_path.name, '-C', '%(avrconf)s']
        if extra_flags is not None:
            flags.extend(extra_flags)

        try:
            cwd = os.getcwd()
            os.chdir(hex_path.parent)
            stdout, stderr = self._run_command(flags)
        finally:
            os.chdir(cwd)
        print stdout
        print stderr
        return stdout, stderr

    def test_connection(self, port, baud_rate):
        '''
        This method is called by the `get_port` method for each available
        serial-port on the system until a value of `True` is returned.
        '''
        flags = ['-c', self.protocol, '-b', str(baud_rate), '-p',
                 self.microcontroller, '-P', port, '-C', '%(avrconf)s', '-n']
        try:
            self._run_command(flags)
        except (ConnectionError, CalledProcessError):
            return False
        return True
