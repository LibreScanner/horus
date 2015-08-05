# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import platform
s = platform.system()
del platform

def isLinux():
	return s == 'Linux'

def isDarwin():
	return s == 'Darwin'

def isWindows():
	return s == 'Windows'