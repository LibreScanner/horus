# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014-2015 Mundo Reader S.L.                             #
#                                                                       #
# Date: November 2014                                                   #
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

import threading

from horus.engine.board import Board
from horus.engine.camera import Camera

from horus.engine.board import WrongFirmware, BoardNotConnected
from horus.engine.camera import CameraNotConnected, WrongCamera, InvalidVideo

import horus.util.error as Error
from horus.util.singleton import Singleton


@Singleton
class Driver:
	"""Driver class. For managing scanner hw"""
	def __init__(self):
		self.isConnected = False

		#TODO: Callbacks to Observer pattern
		self.beforeCallback = None
		self.afterCallback = None

		self.unplugged = False

		self.board = Board(self)
		self.camera = Camera(self)

	def setCallbacks(self, before, after):
		self.beforeCallback = before
		self.afterCallback = after

	def connect(self):
		if self.beforeCallback is not None:
			self.beforeCallback()
		threading.Thread(target=self._connect, args=(self.afterCallback,)).start()

	def _connect(self, callback):
		error = None
		self.isConnected = False
		try:
			self.camera.connect()
			self.board.connect()
		except WrongFirmware:
			error = Error.WrongFirmware
		except BoardNotConnected:
			error = Error.BoardNotConnected
		except CameraNotConnected:
			error = Error.CameraNotConnected
		except WrongCamera:
			error = Error.WrongCamera
		except InvalidVideo:
			error = Error.InvalidVideo
		else:
			self.isConnected = True
		finally:
			if error is None:
				self.unplugged = False
				response = (True, self.isConnected)
			else:
				response = (False, error)
				self.disconnect()
			if callback is not None:
				callback(response)
		
	def disconnect(self):
		self.isConnected = False
		self.camera.disconnect()
		self.board.disconnect()