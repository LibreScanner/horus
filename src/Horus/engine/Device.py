#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#																		#
# This file is part of the Horus Project								#
#																		#
# Copyright (C) 2014 Mundo Reader S.L. 									#
# 																		#
# Date: March 2014														#
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>					#
#																		#
# This program is free software: you can redistribute it and/or modify	#
# it under the terms of the GNU General Public License as published by	#
# the Free Software Foundation, either version 3 of the License, or 	#
# (at your option) any later version. 									#
#																		#
# This program is distributed in the hope that it will be useful,		#
# but WITHOUT ANY WARRANTY; without even the implied warranty of		#
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 			#
# GNU General Public License for more details. 							#
#																		#
# You should have received a copy of the GNU General Public License 	#
# along with this program. If not, see <http://www.gnu.org/licenses/>. 	#
#																		#
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
  
	def __init__(self, serial_name, degrees, delay):
		"""Arguments: motor step, motor pulse delay"""
		self.serial_name = serial_name  #-- Serial Name
		self.degrees = degrees   #-- Motor step
		self.delay = delay   #-- Motor pulse delay
    

	def Connect(self):
		""" Opens serial port and performs handshake"""
		try:
			self.serial_port = serial.Serial(self.serial_name, 921600, timeout=1)
			time.sleep(2)
			if self.serial_port.isOpen():
				self.PerformHandshake()
			else:
				print 'Serial port is not connected.'
		except serial.SerialException:
			sys.stderr.write("Error opening the port {0}".format(self.serial_name))
			
	def Disconnect(self):
		""" Closes serial port """
		try:
			if self.serial_port.isOpen():
				self.serial_port.close()
		except serial.SerialException:
			sys.stderr.write("Error closing the port {0}".format(self.serial_name))


	def SetMotorCW(self):
		"""Performs a motor step clockwise"""
		self.SendCommand(133) # 10000101
		#ack = self.serial_port.read() # TODO: use ack
    
	def SetMotorCCW(self):
		"""Performs a motor step counterclockwise"""
		self.SendCommand(137) # 10001001
		#ack = self.serial_port.read() # TODO: use ack
   
	def SetRightLaserOn(self):
		"""Turns right laser on"""
		self.SendCommand(149) # 10010101
		#ack = self.serial_port.read() # TODO: use ack
	 
	def SetLeftLaserOn(self):
		"""Turns left laser on"""
		self.SendCommand(165) # 10100101
		#ack = self.serial_port.read() # TODO: use ack
	
	def SetBothLaserOn(self):
		"""Turns both laser on"""
		self.SendCommand(181) # 10110101
		#ack = self.serial_port.read() # TODO: use ack
	
	def SetRightLaserOff(self):
		"""Turns right laser on"""
		self.SendCommand(145) # 10010001
		#ack = self.serial_port.read() # TODO: use ack
	 
	def SetLeftLaserOff(self):
		"""Turns left laser on"""
		self.SendCommand(161) # 10100001
		#ack = self.serial_port.read() # TODO: use ack
	
	def SetBothLaserOff(self):
		"""Turns both laser on"""
		self.SendCommand(177) # 10110001
		#ack = self.serial_port.read() # TODO: use ack

    
	def SendCommand(self, cmd):
		"""Sends the command"""
		self.serial_port.write(chr(cmd))
    
	def PerformHandshake(self):
		"""Sends the config message
				- degrees: motor step in degrees (00.00 - 99.99)
				- delay: motor pulse delay (0 - 99999)
			Receives ack ("bq")
		"""
		frame = 'b{0:0>4}{1:0>5}q\n'.format(trunc(self.degrees * 100), self.delay) #[-10:]
		self.serial_port.write(frame)
		ack = self.serial_port.readline()
		if ack != 'bq\n':
			print "Handshake error. Please Reset the microcontroller."
