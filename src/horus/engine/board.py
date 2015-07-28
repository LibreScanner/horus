#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014-2015 Mundo Reader S.L.                             #
#                                                                       #
# Date: August,November 2014, July 2015                                 #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 2 of the License, or     #
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

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl.html"

import time
import serial
import threading


class Error(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class WrongFirmware(Error):

    def __init__(self, msg="Wrong Firmware"):
        super(Error, self).__init__(msg)


class BoardNotConnected(Error):

    def __init__(self, msg="Board Not Connected"):
        super(Error, self).__init__(msg)


class Board:

    """Board class. For accessing to the scanner board

    Gcode commands:

        G1 Fnnn : feed rate
        G1 Xnnn : move motor

        M70 Tn  : switch off laser n
        M71 Tn  : switch on laser n

        M50 Tn  : read ldr sensor

    """

    def __init__(self, parent=None, serial_name='/dev/ttyUSB0', baud_rate=115200):
        self.parent = parent
        self.serial_name = serial_name
        self.baud_rate = baud_rate

        self._serial_port = None
        self._is_connected = False
        self._motor_position = 0
        self._motor_speed = 0
        self._motor_acceleration = 0
        self._motor_direction = 1
        self._unplug_callback = None
        self._tries = 0  # Check if command fails

    def connect(self):
        """Open serial port and perform handshake"""
        print ">>> Connecting board {0} {1}".format(self.serial_name, self.baud_rate)
        self._is_connected = False
        try:
            self._serial_port = serial.Serial(self.serial_name, self.baud_rate, timeout=2)
            if self._serial_port.isOpen():
                self._reset()  # Force Reset and flush
                version = self._serial_port.readline()
                if version == "Horus 0.1 ['$' for help]\r\n":
                    self.motor_speed(1)
                    self.motor_absolute(0)
                    self._serial_port.timeout = 0.05
                    self._is_connected = True
                    print ">>> Done"
                else:
                    raise WrongFirmware()
            else:
                raise BoardNotConnected()
        except:
            print "Error opening the port {0}\n".format(self.serial_name)
            self._serial_port = None
            raise BoardNotConnected()

    def disconnect(self):
        """Close serial port"""
        if self._is_connected:
            print ">>> Disconnecting board {0}".format(self.serial_name)
            try:
                if self._serial_port is not None:
                    self.left_laser_off()
                    self.right_laser_off()
                    self.motor_enable()
                    self._serial_port.close()
                    del self._serial_port
            except serial.SerialException:
                print "Error closing the port {0}\n".format(self.serial_name)
                print ">>> Error"
            self._is_connected = False
            print ">>> Done"

    def set_unplug_callback(self, value):
        self._unplug_callback = value

    def motor_invert(self, value):
        if value:
            self._direction = -1
        else:
            self._direction = +1

    def motor_relative(self, value):
        self._motor_position += value * self._direction

    def motor_absolute(self, value):
        self._motor_position = value

    def motor_speed(self, value):
        self._motor_speed = value
        self._send_command("G1F{0}".format(value))

    def motor_acceleration(self, value):
        self._motor_acceleration = value
        self._send_command("$120={0}".format(value))

    def motor_enable(self):
        self._send_command("M17")

    def motor_disable(self):
        self._send_command("M18")

    def left_laser_on(self):
        self._send_command("M71T1")

    def left_laser_off(self):
        self._send_command("M70T1")

    def right_laser_on(self):
        self._send_command("M71T2")

    def right_laser_off(self):
        self._send_command("M70T2")

    def ldr_sensor(self, pin):
        value = self._send_command("M50T" + pin, read_lines=True).split("\n")[0]
        try:
            return int(value)
        except ValueError:
            return 0

    def motor_move(self, nonblocking=False, callback=None):
        self.send_command("G1X{0}".format(self._motor_position), nonblocking, callback)

    def send_command(self, req, nonblocking=False, callback=None, read_lines=False):
        if nonblocking:
            threading.Thread(target=self._send_command, args=(req, callback, read_lines)).start()
        else:
            self._send_command(req, callback, read_lines)

    def _send_command(self, req, callback=None, read_lines=False):
        """Sends the request and returns the response"""
        ret = ''
        if self._is_connected and req != '':
            if self._serial_port is not None and self._serial_port.isOpen():
                try:
                    self._serial_port.flushInput()
                    self._serial_port.flushOutput()
                    self._serial_port.write(req + "\r\n")
                    while ret == '':  # TODO: add timeout
                        if read_lines:
                            ret = ''.join(self._serial_port.readlines())
                        else:
                            ret = ''.join(self._serial_port.readline())
                        time.sleep(0.01)
                    self._success()
                except:
                    if callback is not None:
                        callback(ret)
                    self._fail()
            else:
                self._fail()
        if callback is not None:
            callback(ret)
        return ret

    def _success(self):
        self._tries = 0

    def _fail(self):
        self._tries += 1
        if self._tries >= 1:
            self._tries = 0
            if self._unplug_callback is not None and \
               self.parent is not None and \
               not self.parent.unplugged:
                self.parent.unplugged = True
                self._unplug_callback()

    def _reset(self):
        self._serial_port.flushInput()
        self._serial_port.flushOutput()
        self._serial_port.write("\x18\r\n")  # Ctrl-x
        self._serial_port.readline()
