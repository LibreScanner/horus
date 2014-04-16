#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: March 2014                                                      #
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
	ASCII Protocol

		-> bddddmmmmq\n
		<- bq\n
		
	dddd : motor step * 100 (degrees)
	mmmm : motor pulse delay (us)

	Binary Protocol

		-> 10ccvv01

	cc : command

		00 : motor
		01 : laser right
		10 : laser left
		11 : laser right & left
		
	vv : value

		laser:
			X0 : off
			X1 : on
		motor:
			00 : no operation
			01 : step cw
			10 : step ccw
			11 : no operation
	"""
  
	def __init__(self, serialName, degrees, delay):
		"""Arguments: motor step, motor pulse delay"""
		print ">>> Initializing device ..."
		print " - Serial Name: {0}".format(serialName)
		print " - Step Degrees: {0}".format(degrees)
		print " - Step Delay: {0}".format(delay)
		self.serialName = serialName
		self.degrees = degrees 	#-- Motor step
		self.delay = delay   	#-- Motor pulse delay
   		print ">>> Done"

	def connect(self):
		""" Opens serial port and performs handshake"""
		print ">>> Connecting device ..."
		try:
			self.serialPort = serial.Serial(self.serialName, 921600, timeout=1)
			time.sleep(2)
			if self.serialPort.isOpen():
				self.performHandshake()
			else:
				print 'Serial port is not connected.'
		except serial.SerialException:
			sys.stderr.write("Error opening the port {0}\n".format(self.serialName))
			self.serialPort = None
			return False
		print ">>> Done"
		return True

	def disconnect(self):
		""" Closes serial port """
		print ">>> Disconnecting device ..."
		try:
			if self.serialPort != None:
				if self.serialPort.isOpen():
					self.serialPort.close()
		except serial.SerialException:
			sys.stderr.write("Error closing the port {0}\n".format(self.serialName))
			return False
		print ">>> Done"
		return True

	def enable(self):
		"""Enables motor"""
		self.sendCommand(141) # 10001101
		#ack = self.serialPort.read() # TODO: use ack

	def disable(self):
		"""Disables motor"""
		self.sendCommand(129) # 10000001
		#ack = self.serialPort.read() # TODO: use ack

	def enable(self):
		"""Enables motor"""
		self.sendCommand(141) # 10001101
		#ack = self.serialPort.read() # TODO: use ack

	def disable(self):
		"""Disables motor"""
		self.sendCommand(129) # 10000001
		#ack = self.serialPort.read() # TODO: use ack

	def setMotorCW(self):
		"""Performs a motor step clockwise"""
		self.sendCommand(133) # 10000101
		#ack = self.serialPort.read() # TODO: use ack
    
	def setMotorCCW(self):
		"""Performs a motor step counterclockwise"""
		self.sendCommand(137) # 10001001
		#ack = self.serialPort.read() # TODO: use ack
   
	def setRightLaserOn(self):
		"""Turns right laser on"""
		self.sendCommand(149) # 10010101
		#ack = self.serialPort.read() # TODO: use ack
	 
	def setLeftLaserOn(self):
		"""Turns left laser on"""
		self.sendCommand(165) # 10100101
		#ack = self.serialPort.read() # TODO: use ack
	
	def setBothLaserOn(self):
		"""Turns both laser on"""
		self.sendCommand(181) # 10110101
		#ack = self.serialPort.read() # TODO: use ack
	
	def setRightLaserOff(self):
		"""Turns right laser on"""
		self.sendCommand(145) # 10010001
		#ack = self.serialPort.read() # TODO: use ack
	 
	def setLeftLaserOff(self):
		"""Turns left laser on"""
		self.sendCommand(161) # 10100001
		#ack = self.serialPort.read() # TODO: use ack
	
	def setBothLaserOff(self):
		"""Turns both laser on"""
		self.sendCommand(177) # 10110001
		#ack = self.serialPort.read() # TODO: use ack

	def sendCommand(self, cmd):
		"""Sends the command"""
		self.serialPort.write(chr(cmd))
    
	def performHandshake(self):
		"""Sends the config message
				- degrees: motor step in degrees (00.00 - 99.99)
				- delay: motor pulse delay (0 - 99999)
			Receives ack ("bq")
		"""
		frame = 'b{0:0>4}{1:0>5}q\n'.format(trunc(self.degrees * 100), self.delay) #[-10:]
		self.serialPort.write(frame)
		ack = self.serialPort.readline()
		if ack != 'bq\n':
			print "Handshake error. Please Reset the microcontroller or reload the firmware"
