#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014-2015 Mundo Reader S.L.                             #
#                                                                       #
# Date: November 2014, July 2015                                        #
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


WrongFirmware = "Wrong Firmware"
BoardNotConnected = "Board Not Connected"
CameraNotConnected = "Camera Not Connected"
WrongCamera = "Wrong Camera"
InvalidVideo = "Invalid Video"
PatternNotDetected = "Pattern Not Detected"
WrongMotorDirection = "Wrong Motor Direction"
LaserNotDetected = "Laser Not Detected"
WrongLaserPosition = "Wrong Laser Position"
CalibrationError = "Calibration Error"
CalibrationCanceled = "Calibration Canceled"
ScanError = "Scan Error"


# Define a fake _() function to fake the gettext tools in to generating
# strings for the profile settings.
def _(n):
    return n

_("Wrong Firmware")
_("Board Not Connected")
_("Camera Not Connected")
_("Wrong Camera")
_("Invalid Video")
_("Pattern Not Detected")
_("Wrong Motor Direction")
_("Laser Not Detected")
_("Wrong Laser Position")
_("Calibration Error")
_("Calibration Canceled")
_("Scan Error")

del _
