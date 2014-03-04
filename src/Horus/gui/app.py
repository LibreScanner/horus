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

import wx._core

from Horus.gui import mainWindow

class HorusApp(wx.App):
	def __init__(self):
		super(HorusApp, self).__init__(redirect=False)

		# TODO: Load Profile and Preferences

		self.mainWindow = mainWindow.mainWindow()
		self.mainWindow.Show()