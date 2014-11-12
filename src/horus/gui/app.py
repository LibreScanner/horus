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

import os
import wx._core

from horus.util import profile, resources

from horus.gui.main import MainWindow
from horus.gui.splash import SplashScreen
from horus.gui.welcome import WelcomeWindow

class HorusApp(wx.App):
	def __init__(self):
		super(HorusApp, self).__init__(redirect=False)

		self.basePath = profile.getBasePath()

		SplashScreen(self.afterSplashCallback)

	def afterSplashCallback(self):
		#-- Load Profile and Preferences
		profile.loadPreferences(os.path.join(self.basePath, 'preferences.ini'))
		profile.loadProfile(os.path.join(self.basePath, 'current-profile.ini'))
		profile.putPreference('workbench', 'scanning')

		#-- Load Language
		resources.setupLocalization(profile.getPreference('language'))

		#-- Create Main Window
		mainWindow = MainWindow()

		if profile.getPreferenceBool('show_welcome'):
			#-- Create Welcome Window
			welcome = WelcomeWindow(mainWindow)

	def __del__(self):
		#-- Save Profile and Preferences
		profile.savePreferences(os.path.join(self.basePath, 'preferences.ini'))
		profile.saveProfile(os.path.join(self.basePath, 'current-profile.ini'))