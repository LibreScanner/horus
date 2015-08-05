# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

##                    ##
##-- TODO: refactor --##
##                    ##

import os
import system as sys
import resources
from subprocess import Popen, PIPE, STDOUT

from pathHelpers import path
from serialDevice import SerialDevice

class FirmwareError(Exception):
    pass

class AvrDude(SerialDevice):
    def __init__(self, protocol="arduino", microcontroller="atmega328p", baudRate="19200", confPath=None, port=None):
        self.protocol = protocol
        self.microcontroller = microcontroller
        self.baudRate = baudRate

        if sys.isWindows():
        	self.avrdude = path(resources.getPathForTools("avrdude.exe")).abspath()
        elif sys.isDarwin():
            self.avrdude = path(resources.getPathForTools("avrdude")).abspath()
        else:
            self.avrdude = 'avrdude'
        
        if self.avrdude is None:
            raise FirmwareError('avrdude not installed')

        if confPath is None:
            self.avrconf = path(resources.getPathForTools("avrdude.conf")).abspath()
        else:
            self.avrconf = path(confPath).abspath()
        
        if port:
            self.port = port
        else:
            self.port = self.get_port(baudRate)

    def _runCommand(self, flags, callback=None):
        config = dict(avrdude=self.avrdude, avrconf=self.avrconf)
        cmd = ['%(avrdude)s'] + flags
        cmd = [v % config for v in cmd]
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        out = ''
        while True:
            char = p.stdout.read(1)
            if not char:
                break
            out += char
            if char == '#':
                if callback is not None:
                    callback()
        return out

    def flash(self, hexPath=None, extraFlags=None, callback=None):
        if hexPath is None:
            hexPath = resources.getPathForFirmware("horus-fw.hex")
        hexPath = path(hexPath)
        flags = ['-c', self.protocol, '-b', str(self.baudRate), '-p',
                 self.microcontroller, '-P', '%s' % self.port, '-U',
                 'flash:w:%s:i' % hexPath.name, '-C', '%(avrconf)s']
        if extraFlags is not None:
            flags.extend(extraFlags)
        try:
            cwd = os.getcwd()
            os.chdir(hexPath.parent)
            out = self._runCommand(flags, callback)
        finally:
            os.chdir(cwd)
        return out