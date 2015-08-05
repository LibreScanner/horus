# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


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
