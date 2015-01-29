#!/usr/bin/python
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


WrongFirmware       = "wrong_firmware"
BoardNotConnected   = "board_not_connected"
CameraNotConnected  = "camera_not_connected"
WrongCamera         = "wrong_camera"
InvalidVideo        = "invalid_video"
CalibrationError    = "calibration_error"
CalibrationCanceled = "calibration_canceled"
ScanError           = "scan_error"

#Define a fake _() function to fake the gettext tools in to generating strings for the error messages.
def _(n):
	return n

_dict = { 
	WrongFirmware       : _("Wrong Firmware"),
	BoardNotConnected   : _("Board Not Connected"),
	CameraNotConnected  : _("Camera Not Connected"),
	WrongCamera         : _("Wrong Camera"),
	InvalidVideo        : _("Invalid Video"),
	CalibrationError    : _("Calibration Error"),
	CalibrationCanceled : _("Calibration Canceled"),
	ScanError           : _("Scan Error")
}

del _

def contains(key):
	return key in _dict

def str(key):
	if contains(key):
		return _dict[key]