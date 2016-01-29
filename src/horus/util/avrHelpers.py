# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
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

import logging
logger = logging.getLogger(__name__)


class FirmwareError(Exception):
    pass


class AvrDude(SerialDevice):

    def __init__(self, protocol="arduino", microcontroller="atmega328p",
                 baud_rate="19200", conf_path=None, port=None):
        self.protocol = protocol
        self.microcontroller = microcontroller
        self.baud_rate = baud_rate

        if sys.is_windows():
            self.avrdude = path(resources.get_path_for_tools("avrdude.exe")).abspath()
        elif sys.is_darwin():
            self.avrdude = path(resources.get_path_for_tools("avrdude")).abspath()
        else:
            self.avrdude = 'avrdude'

        if self.avrdude is None:
            raise FirmwareError('avrdude not installed')

        if conf_path is None:
            self.avrconf = path(resources.get_path_for_tools("avrdude.conf")).abspath()
        else:
            self.avrconf = path(conf_path).abspath()

        if port:
            self.port = port
        else:
            self.port = self.get_port(baud_rate)

    def _run_command(self, flags, callback=None):
        config = dict(avrdude=self.avrdude, avrconf=self.avrconf)
        cmd = ['%(avrdude)s'] + flags
        cmd = [v % config for v in cmd]
        logger.info(' ' + ' '.join(cmd))
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

    def flash(self, hex_path=None, clear_eeprom=False, callback=None):
        if hex_path is None:
            hex_path = resources.get_path_for_firmware("horus-fw.hex")
        if clear_eeprom:
            hex_path = resources.get_path_for_firmware("eeprom_clear.hex")
        hex_path = path(hex_path)
        flags = ['-C', '%(avrconf)s', '-c', self.protocol, '-p', self.microcontroller,
                 '-P', '%s' % self.port, '-b', str(self.baud_rate), '-D', '-U',
                 'flash:w:%s' % hex_path.name]
        try:
            cwd = os.getcwd()
            os.chdir(hex_path.parent)
            out = self._run_command(flags, callback)
            logger.info(' Upload completed')
        finally:
            os.chdir(cwd)
        return out
