#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: August 2014                                                     #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
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

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v3 http://www.gnu.org/licenses/gpl.html"

import sys
import time
import serial

from math import trunc

class Device:
	"""Device class. For accessing to the scanner device"""
	"""
	Gcode commands:

		G1 Fnnn : feed rate
		G1 Xnnn : move motor

		M70 Tn  : switch off laser n
		M71 Tn  : switch on laser n

	"""
  
	def __init__(self, serialName='/dev/ttyACM0'):
		""" """
		print ">>> Initializing device ..."
		print " - Serial Name: {0}".format(serialName)
		self.serialName = serialName
		self.serialPort = None
		self._position = 0
   		print ">>> Done"

	def connect(self):
		""" Opens serial port and performs handshake"""
		print ">>> Connecting device ..."
		try:
			self.serialPort = serial.Serial(self.serialName, 9600, timeout=2)
			if self.serialPort.isOpen():

				#-- Force Reset and flush
				self.serialPort.setDTR(False)
				time.sleep(0.022)
				self.serialPort.flushInput()
				self.serialPort.flushOutput()
				self.serialPort.setDTR(True)

				tries = 20
				#-- Check Handshake
				while tries:
					version = self.serialPort.readline()
					if len(version) > 20:
						break
					tries -= 1
					time.sleep(0.1)
				if version == "Grbl 0.9g ['$' for help]\r\n":
					self.setSpeedMotor(1)
					self.setAbsolutePosition(0)
					#self.enable()
				else:
					print ">>> Error"
					return False
			else:
				print "Serial port is not connected."
				print ">>> Error"
				return False
		except serial.SerialException:
			sys.stderr.write("Error opening the port {0}\n".format(self.serialName))
			self.serialPort = None
			print ">>> Error"
			return False
		print ">>> Done"
		return True

	def disconnect(self):
		""" Closes serial port """
		print ">>> Disconnecting device ..."
		try:
			if self.serialPort is not None:
				if self.serialPort.isOpen():
					self.serialPort.close()
		except serial.SerialException:
			sys.stderr.write("Error closing the port {0}\n".format(self.serialName))
			print ">>> Error"
			return False
		print ">>> Done"
		return True

	def enable(self):
		"""Enables motor"""
		return self.sendCommand("M17")

	def disable(self):
		"""Disables motor"""
		return self.sendCommand("M18")

	def setSpeedMotor(self, feedRate):
		"""Sets motor feed rate"""
		self.feedRate = feedRate
		return self.sendCommand("G1F{0}".format(self.feedRate))

	def setAccelerationMotor(self, acceleration):
		"""Sets motor acceleration"""
		self.acceleration = acceleration
		return self.sendCommand("$120={0}".format(self.acceleration))

	def setRelativePosition(self, pos):
		self._position += pos

	def setAbsolutePosition(self, pos):
		self._position = pos

	def setMoveMotor(self):
		"""Moves the motor"""
		self.sendCommand("G1X{0}".format(self._position))
   
	def setRightLaserOn(self):
		"""Turns right laser on"""
		self.sendCommand("M71T1", ret=False)
	 
	def setLeftLaserOn(self):
		"""Turns left laser on"""
		self.sendCommand("M71T2", ret=False)
	
	def setRightLaserOff(self):
		"""Turns right laser off"""
		self.sendCommand("M70T1", ret=False)
	 
	def setLeftLaserOff(self):
		"""Turns left laser off"""
		self.sendCommand("M70T2", ret=False)

	def sendCommand(self, cmd, ret=True, readLines=False):
		"""Sends the command"""
		if self.serialPort is not None and self.serialPort.isOpen():
			self.serialPort.flushInput()
			self.serialPort.write(cmd+"\r\n")
			if ret:
				if readLines:
					return ''.join(self.serialPort.readlines())
				else:
					return ''.join(self.serialPort.readline())
		else:
			print "Serial port is not connected."

	def _checkAcknowledge(self, ack):
		return ack.endswith("\r\n") #ok