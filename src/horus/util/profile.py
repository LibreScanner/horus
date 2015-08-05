#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014-2015 Mundo Reader S.L.                             #
# Copyright (C) 2013 David Braam from Cura Project                      #
#                                                                       #
# Date: June 2014                                                       #
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
import traceback
import math
import numpy
import re
import zlib
import base64
import sys
import types

if sys.version_info[0] < 3:
	import ConfigParser
else:
	import configparser as ConfigParser

from horus.util import system, resources


# TODO: Make this class inherit from dict or iterable to be able to gen len, values, access with [], etc.
# TODO: Try to erase tag -> Used to hide panels
# TODO: Raise error if setting id already exists in dictionary
# TODO: Change to "preferences" and "machine_settings"+
class Settings():

	def __init__(self):
		self.settings = {}

	def addSetting(setting):
		self.settings[setting.id, setting]

	def populateSettings():

		self.addSetting(Setting('serial_name', _('Serial Name'), 'profile', str, '/dev/ttyUSB0'))
		self.addSetting(Setting('baud_rate', _('Baud rate'), 'profile', (9600, 14400, 19200, 38400, 57600, 115200), 115200))
		self.addSetting(Setting('camera_id', _('Camera Id'), 'profile', str, '/dev/video0'))
		self.addSetting(Setting('board', _('Board'), 'profile', ('Arduino Uno', 'BT ATmega328'), 'BT ATmega328'))
		self.addSetting(Setting('invert_motor', _('Invert motor'), 'profile', bool, False))

		# Hack to translate combo boxes:
		_('High')
		_('Medium')
		_('Low')
		self.addSetting(Setting('luminosity', _('Luminosity'), 'profile', ('High', 'Medium', 'Low'), 'Medium'))
		self.addSetting(Setting('brightness_control', _('Brightness'), 'profile', int, 128, min_value=0, max_value=255))
		self.addSetting(Setting('contrast_control', _('Contrast'), 'profile', int, 32, min_value=0, max_value=255))
		self.addSetting(Setting('saturation_control', _('Saturation'), 'profile', int, 32, min_value=0, max_value=255))
		self.addSetting(Setting('exposure_control', _('Exposure'), 'profile', int, 16, min_value=1, max_value=512))
		# TODO: Contemplate this type of settings. Validate that the value (int) is within the possible values
		# self.addSetting(Setting('framerate_control', str('30'), [str('30'), str('25'), str('20'), str('15'), str('10'), str('5')], 'profile', _('Framerate'))
		self.addSetting(Setting('framerate_control', _('Framerate'), 'profile', (30, 25, 20, 15, 10, 5), 30))
		self.addSetting(Setting('resolution_control', _('Resolution'), 'profile', ('1280x960', '960x720', '800x600', '320x240', '160x120'), '1280x960'))
		self.addSetting(Setting('use_distortion_control', _('Use Distortion'), 'profile', bool, False))
		self.addSetting(Setting('step_degrees_control', _('Step Degrees'), 'profile', float, -0.45, min_value=0.01)
		self.addSetting(Setting('feed_rate_control', _('Feed Rate'), 'profile', int, 200, min_value=1, max_value=1000))
		self.addSetting(Setting('acceleration_control', _('Acceleration'), 'profile', int, 200, min_value=1, max_value=1000))

		self.addSetting(Setting('brightness_calibration', _('Brightness'), 'profile', int, 100, min_value=0, max_value=255))
		self.addSetting(Setting('contrast_calibration', _('Contrast'), 'profile', int, 32, min_value=0, max_value=255))
		self.addSetting(Setting('saturation_calibration', _('Saturation'), 'profile', int, 100, min_value=0, max_value=255))
		self.addSetting(Setting('exposure_calibration', _('Exposure'), 'profile', int, 16, min_value=1, max_value=512))
		self.addSetting(Setting('framerate_calibration', _('Framerate'), 'profile', (30, 25, 20, 15, 10, 5), 30))
		self.addSetting(Setting('resolution_calibration', _('Resolution'), 'profile', ('1280x960', '960x720', '800x600', '320x240', '160x120'), '1280x960'))
		self.addSetting(Setting('use_distortion_calibration', _('Use Distortion'), 'profile', bool, False))

		# Hack to translate combo boxes:
		_('Simple Scan')
		_('Texture Scan')
		self.addSetting(Setting('scan_type', _('Scan'), 'profile', ('Simple Scan', 'Texture Scan'), 'Texture Scan'))
		# Hack to translate combo boxes:
		_('Left')
		_('Right')
		_('Both')
		self.addSetting(Setting('use_laser', _('Use Laser'), 'profile', ('Left', 'Right', 'Both'), 'Both'))
		self.addSetting(Setting('fast_scan', _('Fast Scan (experimental)'), 'profile', bool, False))

		self.addSetting(Setting('step_degrees_scanning', _('Step Degrees'), 'profile', float, 0.45, min_value=0.01))
		self.addSetting(Setting('feed_rate_scanning', _('Feed Rate'), 'profile', int, 200, min_value=1, max_value=1000))
		self.addSetting(Setting('acceleration_scanning', _('Acceleration'), 'profile', int, 300, min_value=1, max_value=1000))
		self.addSetting(Setting('brightness_scanning', _('Brightness'), 'profile', int, 100, min_value=0, max_value=255))
		self.addSetting(Setting('contrast_scanning', _('Contrast'), 'profile', int, 32, min_value=0, max_value=255))
		self.addSetting(Setting('saturation_scanning', _('Saturation'), 'profile', int, 32, min_value=0, max_value=255))
		self.addSetting(Setting('laser_exposure_scanning', _('Exposure'), 'profile', int, 6, min_value=1, max_value=512, tag='simple'))
		self.addSetting(Setting('color_exposure_scanning', _('Exposure'), 'profile', int, 10, min_value=1, max_value=512, tag='texture'))
		self.addSetting(Setting('framerate_scanning', _('Framerate'), 'profile', (30, 25, 20, 15, 10, 5), 30))
		self.addSetting(Setting('resolution_scanning', _('Resolution'), 'profile', ('1280x960', '960x720', '800x600', '320x240', '160x120'), '1280x960'))
		self.addSetting(Setting('use_distortion_scanning', _('Use Distortion'), 'profile', bool, False))

		# Hack to translate combo boxes:
		_('Laser')
		_('Gray')
		_('Line')
		_('Color')
		self.addSetting(Setting('img_type', _('Image Type'), 'profile', ('Laser', 'Gray', 'Line', 'Color'), 'Laser'))
		self.addSetting(Setting('use_open', _('Use Open'), 'profile', bool, True, tag='texture'))
		self.addSetting(Setting('open_value', _('Open'), 'profile', int, 2, min_value=1, max_value=10, tag='texture'))
		self.addSetting(Setting('use_threshold', _('Use Threshold'), 'profile', bool, True, tag='texture'))
		self.addSetting(Setting('threshold_value', _('Threshold'), 'profile', int, 25, min_value=0, max_value=255, tag='texture'))
		self.addSetting(Setting('use_cr_threshold', _('Use Threshold'), 'profile', bool, True, tag='simple'))
		self.addSetting(Setting('cr_threshold_value', _('Threshold'), 'profile', int, 140, min_value=0, max_value=255, tag='simple'))
		self.addSetting(Setting('point_cloud_color', _('Choose Point Cloud Color'), 'profile', str, 'AAAAAA'))
		self.addSetting(Setting('adjust_laser', _('Adjust Laser'), 'profile', bool, True))
		self.addSetting(Setting('camera_matrix', _('Calibration Matrix'), 'profile', numpy.ndarray, ([[1425.0,0.0,480.0],[0.0,1425.0,640.0],[0.0,0.0,1.0]])))
		self.addSetting(Setting('distortion_vector', _('Distortion Vector'), 'profile', numpy.ndarray, ([0.0,0.0,0.0,0.0,0.0]))

		self.addSetting(Setting('laser_threshold_value', _('Laser Threshold'), 'profile', int, 120, min_value=0, max_value=255))
		self.addSetting(Setting('distance_left', _('Distance'), 'profile', float, 0.0))
		self.addSetting(Setting('normal_left', _('Normal'), 'profile', numpy.ndarray, ([0.0,0.0,0.0])))
		self.addSetting(Setting('distance_right', _('Distance'), 'profile', float, 0.0))
		self.addSetting(Setting('normal_right', _('Normal'), 'profile', numpy.ndarray, ([0.0,0.0,0.0])))
		self.addSetting(Setting('rotation_matrix', _('Rotation Matrix'), 'profile', numpy.ndarray, ([[0.0,1.0,0.0],[0.0,0.0,-1.0],[-1.0,0.0,0.0]])))
		self.addSetting(Setting('translation_vector', _('Translation Matrix'), 'profile', numpy.ndarray, ([5.0,80.0,320.0])))

		self.addSetting(Setting('pattern_rows', _('Pattern Rows'), 'profile', int, 6))
		self.addSetting(Setting('pattern_columns', _('Pattern Columns'), 'profile', int, 11))
		self.addSetting(Setting('square_width', _('Square width'), 'profile', int, 13))
		self.addSetting(Setting('pattern_distance', _('Pattern Distance'), 'profile', float, 0))
		self.addSetting(Setting('extrinsics_step', _('Extrinsics Step'), 'profile', float, -5.0))

		self.addSetting(Setting('laser_coordinates', _('Laser Coordinates'), 'profile', numpy.ndarray, ([[480.0,480.0],[480.0,480.0]])))
		self.addSetting(Setting('laser_origin', _('Laser Origin'), 'profile', numpy.ndarray, ([0.0,0.0,0.0])))
		self.addSetting(Setting('laser_normal', _('Laser Normal'), 'profile', numpy.ndarray, ([0.0,0.0,0.0])))

		# self.addSetting(Setting('left_button', _('Left'), 'profile', str, 'profile', False))
		# self.addSetting(Setting('right_button', '', str, 'profile', _('Right'), False))
		# self.addSetting(Setting('move_button', '', str, 'profile', _('Move'), False))
		# self.addSetting(Setting('enable_button', '', str, 'profile', _('Enable'), False))
		# self.addSetting(Setting('gcode_gui', '', str, 'profile', _('Send'), False))
		# self.addSetting(Setting('ldr_value', '', str, 'profile', _('Send'), False))

		self.addSetting(Setting('machine_diameter', _('Machine Diameter'), 'machine_setting', float, 200.0))
		self.addSetting(Setting('machine_width', _('Machine Width'), 'machine_setting', float, 200.0))
		self.addSetting(Setting('machine_height', _('Machine Height'), 'machine_setting', float, 200.0))
		self.addSetting(Setting('machine_depth', _('Machine Depth'), 'machine_setting', float, 200.0))
		self.addSetting(Setting('machine_shape', _('Machine Shape'), 'machine_setting', ('Circular', 'Rectangular'), 'Circular'))
		self.addSetting(Setting('machine_model_path', _('Machine Model'), str, resources.getPathForMesh('ciclop_platform.stl')))

		self.addSetting(Setting('view_roi', _('View ROI'), 'machine_setting', bool, False))
		self.addSetting(Setting('roi_diameter', _('Diameter'), 'machine_setting', int, 200, min_value=0, max_value=250))
		self.addSetting(Setting('roi_width', _('Width'), 'machine_setting', int, 200, min_value=0, max_value=250))
		self.addSetting(Setting('roi_height', _('Height'), 'machine_setting', int, 200, min_value=0, max_value=250))
		self.addSetting(Setting('roi_depth', _('Depth'), 'machine_setting', int, 200, min_value=0, max_value=250))

		##-- Preferences

		self.addSetting(Setting('language', _('Language'), 'preference', ('English', 'Español', 'Français', 'Deutsch', 'Italiano', 'Português'), 'English', tooltip=_('Change the language in which Horus runs. Switching language requires a restart of Horus')))
		# Hack to translate combo boxes:
		_('Control workbench')
		_('Calibration workbench')
		_('Scanning workbench')
		self.addSetting(Setting('workbench', _('Workbench'), 'preference', ('Control workbench', 'Calibration workbench', 'Scanning workbench'), 'Scanning workbench'))
		self.addSetting(Setting('show_welcome', _('Show Welcome'), 'preference', bool, True))
		self.addSetting(Setting('check_for_updates', _('Check for Updates'), 'preference', bool, True))
		self.addSetting(Setting('basic_mode', _('Basic Mode'), 'preference', bool, False))
		self.addSetting(Setting('view_control_panel', _('View Control Panel'), 'preference', bool, True))
		self.addSetting(Setting('view_control_video', _('View Control Panel') 'preference', bool, True)
		self.addSetting(Setting('view_calibration_panel', _('View Calibration Panel'), 'preference', bool, True))
		self.addSetting(Setting('view_calibration_video', _('View Calibration Video'), 'preference', bool, True))
		self.addSetting(Setting('view_scanning_panel', _('View Scanning Panel'), 'preference', bool, False))
		self.addSetting(Setting('view_scanning_video', _('View Scanning Video'), 'preference', bool, False))
		self.addSetting(Setting('view_scanning_scene', _('View Scanning Scene'), 'preference', bool, True))

		# TODO: change default last file
		self.addSetting(Setting('last_files', _('Last Files'), 'preference', list, []))
		self.addSetting(Setting('last_file', _('Last File'), 'preference', str, '')) # TODO: Set this default value
		self.addSetting(Setting('last_profile', _('Last Profile'), 'preference', str, '')) # TODO: Set this default value
		self.addSetting(Setting('model_color', _('Model color'), 'preference', str, '#888899', tooltip=_('Display color for first extruder')))



class Setting():
	"""
		A setting object contains a configuration setting. These are globally accessible trough the quick access functions
		and trough the settingsDictionary function.
		Settings can be:
		* profile settings (settings that effect the scan process and the scan result)
		* preferences (settings that effect how horus works and acts)
		* machine settings (settings that relate to the physical configuration of your machine)
		Settings have validators that check if the value is valid, but do not prevent invalid values!
		Settings have conditions that enable/disable this setting depending on other settings.
	"""
	def __init__(self, setting_id, label, category, default, setting_type, tooltip='', min_value=None, max_value=None, tag=None):
		self._id = setting_id
		self._label = label
		self._category = category
		self._default = default
		self._type = setting_type
		self._tooltip = tooltip
		self._min_value = min_value
		self._max_value = max_value
		self._tag = tag

		self._value = None

	def getLabel(self):
		return _(self._label)

	def getTooltip(self):
		return _(self._tooltip)

	def setValue(self, value):
		# TODO: Implement this. Check if value is of type _type and that is _min_value <= value <= _max_value
		self._value = value

	def _isValidInt(n):
		try:
			int(eval(n), {}, {}))			
		except:
			return False
		else:
			return True

	def _isValidFloat(n):
		try:
			float(eval(n), {}, {}))			
		except:
			return False
		else:
			return True




#########################################################
## Settings
#########################################################

#Define a fake _() function to fake the gettext tools in to generating strings for the profile settings.
def _(n):
	return n

#-- Settings

settings = Settings()

settings.populateSettings()

#Remove fake defined _() because later the localization will define a global _()
del _

#########################################################
## Settings functions
#########################################################

def getSetting(name):
	"""
		Get the value of a setting.
	:param name: Name of the setting to retrieve.
	:return:     Value of the current setting.
	"""
	global settingsDictionary
	if name in settingsDictionary:
		return settingsDictionary[name].getValue()
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in settings\n' % (name))
	return ''

def getSettingObject(name):
	""" """
	global settingsList
	for set in settingsList:
		if set.getName() is name:
			return set

def putSetting(name, value):
	""" Store a certain value in a setting. """
	global settingsDictionary
	if name in settingsDictionary:
		settingsDictionary[name].setValue(value)

def resetSetting(name):
	""" Reset only the especified setting """
	global settingsDictionary
	if name in settingsDictionary:
		settingsDictionary[name].setValue(settingsDictionary[name]._default)

def getSettingBool(name):
	try:
		setting = getSetting(name)
		return bool(eval(setting, {}, {}))
	except:
		return False

def getSettingInteger(name):
	try:
		setting = getSetting(name)
		return int(eval(setting, {}, {}))
	except:
		return 0

def getSettingMinValue(name):
	global settingsDictionary
	if name in settingsDictionary:
		setting = settingsDictionary[name].getMinValue()
		try:
			return int(eval(setting, {}, {}))
		except:
			return 0
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in settings\n' % (name))
	return ''

def getSettingMaxValue(name):
	global settingsDictionary
	if name in settingsDictionary:
		setting = settingsDictionary[name].getMaxValue()
		try:
			return int(eval(setting, {}, {}))
		except:
			return 0
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in settings\n' % (name))
	return ''

#########################################################
## Profile and preferences functions
#########################################################

## Profile functions
def getBasePath():
	"""
	:return: The path in which the current configuration files are stored. This depends on the used OS.
	"""
	if system.isWindows():
		basePath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
		#If we have a frozen python install, we need to step out of the library.zip
		if hasattr(sys, 'frozen'):
			basePath = os.path.normpath(os.path.join(basePath, ".."))
	else:
		basePath = os.path.expanduser('~/.horus/')
	if not os.path.isdir(basePath):
		try:
			os.makedirs(basePath)
		except:
			print "Failed to create directory: %s" % (basePath)
	return basePath


def loadProfile(filename, allMachines = False):
	"""
		Read a profile file as active profile settings.
	:param filename:    The ini filename to save the profile in.
	:param allMachines: When False only the current active profile is saved. If True all profiles for all machines are saved.
	"""
	global settingsList
	profileParser = ConfigParser.ConfigParser()
	try:
		profileParser.read(filename)
	except ConfigParser.ParsingError:
		return
	if allMachines:
		n = 0
		while profileParser.has_section('profile_%d' % (n)):
			for set in settingsList:
				if set.isPreference() or set.isMachineSetting():
					continue
				section = 'profile_%d' % (n)
				if profileParser.has_option(section, set.getName()):
					set.setValue(unicode(profileParser.get(section, set.getName()), 'utf-8', 'replace'), n)
			n += 1
	else:
		for set in settingsList:
			if set.isPreference() or set.isMachineSetting():
				continue
			section = 'profile'
			if profileParser.has_option(section, set.getName()):
				set.setValue(unicode(profileParser.get(section, set.getName()), 'utf-8', 'replace'))
				
def saveProfile(filename, allMachines = False):
	"""
		Save the current profile to an ini file.
	:param filename:    The ini filename to save the profile in.
	:param allMachines: When False only the current active profile is saved. If True all profiles for all machines are saved.
	"""
	global settingsList
	profileParser = ConfigParser.ConfigParser()
	if allMachines:
		for set in settingsList:
			if set.isPreference() or set.isMachineSetting():
				continue
			for n in xrange(0, getMachineCount()):
				section = 'profile_%d' % (n)
				if not profileParser.has_section(section):
					profileParser.add_section(section)
				profileParser.set(section, set.getName(), set.getValue(n).encode('utf-8'))
	else:
		profileParser.add_section('profile')
		for set in settingsList:
			if set.isPreference() or set.isMachineSetting():
				continue
			if set.isStorable():
				profileParser.set('profile', set.getName(), set.getValue().encode('utf-8'))

	profileParser.write(open(filename, 'w'))




# TODO: Keep checking which of these functions are used..


def resetProfile():
	""" Reset the profile for the current machine to default. """
	for set in settingsList:
		if not set.isProfile():
			continue
		set.setValue(set.getDefault())

def resetProfileSetting(name):
	""" Reset only the especified profile setting """
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isProfile():
		settingsDictionary[name].setValue(settingsDictionary[name]._default)

def setProfileFromString(options):
	"""
	Parse an encoded string which has all the profile settings stored inside of it.
	Used in combination with getProfileString to ease sharing of profiles.
	"""
	options = base64.b64decode(options)
	options = zlib.decompress(options)
	(profileOpts, alt) = options.split('\f', 1)
	global settingsDictionary
	for option in profileOpts.split('\b'):
		if len(option) > 0:
			(key, value) = option.split('=', 1)
			if key in settingsDictionary:
				if settingsDictionary[key].isProfile():
					settingsDictionary[key].setValue(value)
	for option in alt.split('\b'):
		if len(option) > 0:
			(key, value) = option.split('=', 1)
			if key in settingsDictionary:
				settingsDictionary[key].setValue(value)

def getProfileString():
	"""
	Get an encoded string which contains all profile settings.
	Used in combination with setProfileFromString to share settings in files, forums or other text based ways.
	"""
	p = []
	alt = []
	global settingsList
	for set in settingsList:
		if set.isProfile():
			p.append(set.getName() + "=" + set.getValue().encode('utf-8'))
	ret = '\b'.join(p) + '\f' + '\b'.join(alt)
	ret = base64.b64encode(zlib.compress(ret, 9))
	return ret

def insertNewlines(string, every=64): #This should be moved to a better place then profile.
	lines = []
	for i in xrange(0, len(string), every):
		lines.append(string[i:i+every])
	return '\n'.join(lines)

def getPreferencesString():
	"""
	:return: An encoded string which contains all the current preferences.
	"""
	p = []
	global settingsList
	for set in settingsList:
		if set.isPreference():
			p.append(set.getName() + "=" + set.getValue().encode('utf-8'))
	ret = '\b'.join(p)
	ret = base64.b64encode(zlib.compress(ret, 9))
	return ret

def getProfileSettingObject(name):
	""" """
	global settingsList
	for set in settingsList:
		if set.getName() is name:
			return set

#TODO: get profile setting using getType

def getProfileSetting(name):
	"""
		Get the value of an profile setting.
	:param name: Name of the setting to retrieve.
	:return:     Value of the current setting.
	"""
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isProfile():
		return settingsDictionary[name].getValue()
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in profile settings\n' % (name))
	return ''

def getDefaultProfileSetting(name):
	"""
		Get the default value of a profile setting.
	:param name: Name of the setting to retrieve.
	:return:     Value of the current setting.
	"""
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isProfile():
		return settingsDictionary[name].getDefault()
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in profile settings\n' % (name))
	return ''

def getDefaultProfileSettingInteger(name):
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isProfile():
		try:
			setting = settingsDictionary[name].getDefault()
			return int(eval(setting, {}, {}))
		except:
			return 0.0
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in profile settings\n' % (name))
	return ''

def getProfileSettingInteger(name):
	try:
		setting = getProfileSetting(name)
		return int(eval(setting, {}, {}))
	except:
		return 0.0

def getProfileSettingFloat(name):
	try:
		setting = getProfileSetting(name).replace(',', '.')
		return float(eval(setting, {}, {}))
	except:
		return 0.0

def getProfileSettingBool(name):
	try:
		setting = getProfileSetting(name)
		return bool(eval(setting, {}, {}))
	except:
		return False

def getProfileSettingNumpy(name):
	try:
		setting = getProfileSetting(name)

		return numpy.array(eval(setting, {}, {}))
	except:
		return []

def putProfileSetting(name, value):
	""" Store a certain value in a profile setting. """
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isProfile():
		settingsDictionary[name].setValue(value)

def putProfileSettingNumpy(name, value):
	reprValue=repr(value)
	reprValue=reprValue.replace('\n','')
	reprValue=reprValue.replace('array(','')
	reprValue=reprValue.replace(')','')
	reprValue=reprValue.replace(' ','')
	putProfileSetting(name,reprValue)

def isProfileSetting(name):
	""" Check if a certain key name is actually a profile value. """
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isProfile():
		return True
	return False

## Preferences functions
def getPreferencePath():
	"""
	:return: The full path of the preference ini file.
	"""
	return os.path.join(getBasePath(), 'preferences.ini')

def getPreferenceFloat(name):
	"""
	Get the float value of a preference, returns 0.0 if the preference is not a invalid float
	"""
	try:
		setting = getPreference(name).replace(',', '.')
		return float(eval(setting, {}, {}))
	except:
		return 0.0

def getPreferenceBool(name):
	"""
	Get the float value of a preference, returns 0.0 if the preference is not a invalid float
	"""
	try:
		setting = getPreference(name)
		return bool(eval(setting, {}, {}))
	except:
		return False

def getPreferenceColor(name):
	"""
	Get a preference setting value as a color array. The color is stored as #RRGGBB hex string in the setting.
	"""
	colorString = getPreference(name)
	return [float(int(colorString[1:3], 16)) / 255, float(int(colorString[3:5], 16)) / 255, float(int(colorString[5:7], 16)) / 255, 1.0]

def loadPreferences(filename):
	"""
	Read a configuration file as global config
	"""
	global settingsList
	profileParser = ConfigParser.ConfigParser()
	try:
		profileParser.read(filename)
	except ConfigParser.ParsingError:
		return

	for set in settingsList:
		if set.isPreference():
			if profileParser.has_option('preference', set.getName()):
				set.setValue(unicode(profileParser.get('preference', set.getName()), 'utf-8', 'replace'))

def savePreferences(filename):
	global settingsList
	#Save the current profile to an ini file
	parser = ConfigParser.ConfigParser()
	parser.add_section('preference')

	for set in settingsList:
		if set.isPreference():
			parser.set('preference', set.getName(), set.getValue().encode('utf-8'))

	parser.write(open(filename, 'w'))

def getPreference(name):
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isPreference():
		return settingsDictionary[name].getValue()
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in preferences\n' % (name))
	return ''

def putPreference(name, value):
	#Check if we have a configuration file loaded, else load the default.
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isPreference():
		settingsDictionary[name].setValue(value)
		savePreferences(getPreferencePath())
		return
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in preferences\n' % (name))

def isPreference(name):
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isPreference():
		return True
	return False

## Machine functions
def loadMachineSettings(filename):
	global settingsList
	#Read a configuration file as global config
	profileParser = ConfigParser.ConfigParser()
	try:
		profileParser.read(filename)
	except ConfigParser.ParsingError:
		return

	for set in settingsList:
		if set.isMachineSetting():
			if profileParser.has_option('machine_setting', set.getName()):
				set.setValue(unicode(profileParser.get('machine_setting', set.getName()), 'utf-8', 'replace'))

def saveMachineSettings(filename):
	global settingsList
	#Save the current profile to an ini file
	parser = ConfigParser.ConfigParser()
	parser.add_section('machine_setting')

	for set in settingsList:
		if set.isMachineSetting():
			parser.set('machine_setting', set.getName(), set.getValue().encode('utf-8'))

	parser.write(open(filename, 'w'))

def getMachineSettingFileName():
	return 'machine_settings.ini'

def getMachineSetting(name, index = None):
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isMachineSetting():
		return settingsDictionary[name].getValue(index)
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in machine settings\n' % (name))
	return ''

def getMachineSettingObject(name):
	""" """
	global settingsList
	for set in settingsList:
		if set.getName() is name:
			return set

def getMachineSettingBool(name):
	try:
		setting = getMachineSetting(name)
		return bool(eval(setting, {}, {}))
	except:
		return False

def getMachineSettingInteger(name):
	try:
		setting = getMachineSetting(name)
		return int(eval(setting, {}, {}))
	except:
		return 0

def getMachineSettingFloat(name, index = None):
	try:
		setting = getMachineSetting(name, index).replace(',', '.')
		return float(eval(setting, {}, {}))
	except:
		return 0.0

def getMachineSettingPath(name, index = None):
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isMachineSetting():
		value = settingsDictionary[name].getValue(index)
		import os
		if os.path.exists(value):
			return value
		else:
			return getDefaultMachineSetting(name)
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in machine settings\n' % (name))
	return ''

def getDefaultMachineSetting(name):
	"""
		Get the default value of a machine setting.
	:param name: Name of the setting to retrieve.
	:return:     Value of the current setting.
	"""
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isMachineSetting():
		return settingsDictionary[name].getDefault()
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in machine settings\n' % (name))
	return ''

def getDefaultMachineSettingInteger(name):
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isMachineSetting():
		try:
			setting = settingsDictionary[name].getDefault()
			return int(eval(setting, {}, {}))
		except:
			return 0
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in machine settings\n' % (name))
	return ''

def putMachineSetting(name, value):
	""" Store a certain value in a profile setting. """
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isMachineSetting():
		settingsDictionary[name].setValue(value)

def isMachineSetting(name):
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isMachineSetting():
		return True
	return False

def getMachineSettingType(name):
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isMachineSetting():
		return settingsDictionary[name].getType()
	traceback.print_stack()
	sys.stderr.write('Error: "%s" not found in machine settings\n' % (name))
	return ''

#Returns a list of convex polygons, first polygon is the allowed area of the machine,
# the rest of the polygons are the dis-allowed areas of the machine.
def getMachineSizePolygons(machine_shape):
	if machine_shape == "Circular":
		size = numpy.array([getMachineSettingFloat('machine_diameter'), getMachineSettingFloat('machine_diameter'), getMachineSettingFloat('machine_height')], numpy.float32)
	elif machine_shape == "Rectangular":
		size = numpy.array([getMachineSettingFloat('machine_width'), getMachineSettingFloat('machine_depth'), getMachineSettingFloat('machine_height')], numpy.float32)
	return getSizePolygons(size, machine_shape)

def getSizePolygons(size, machine_shape):
	ret = []
	if machine_shape == 'Circular':
		circle = []
		steps = 32
		for n in xrange(0, steps):
			circle.append([math.cos(float(n)/steps*2*math.pi) * size[0]/2, math.sin(float(n)/steps*2*math.pi) * size[1]/2])
		ret.append(numpy.array(circle, numpy.float32))

	elif machine_shape == 'Rectangular':
		rectangle = []
		rectangle.append([-size[0]/2, size[1]/2])
		rectangle.append([size[0]/2, size[1]/2])
		rectangle.append([size[0]/2, -size[1]/2])
		rectangle.append([-size[0]/2, -size[1]/2])
		ret.append(numpy.array(rectangle, numpy.float32))

	w = 20
	h = 20
	ret.append(numpy.array([[-size[0]/2,-size[1]/2],[-size[0]/2+w+2,-size[1]/2], [-size[0]/2+w,-size[1]/2+h], [-size[0]/2,-size[1]/2+h]], numpy.float32))
	ret.append(numpy.array([[ size[0]/2-w-2,-size[1]/2],[ size[0]/2,-size[1]/2], [ size[0]/2,-size[1]/2+h],[ size[0]/2-w,-size[1]/2+h]], numpy.float32))
	ret.append(numpy.array([[-size[0]/2+w+2, size[1]/2],[-size[0]/2, size[1]/2], [-size[0]/2, size[1]/2-h],[-size[0]/2+w, size[1]/2-h]], numpy.float32))
	ret.append(numpy.array([[ size[0]/2, size[1]/2],[ size[0]/2-w-2, size[1]/2], [ size[0]/2-w, size[1]/2-h],[ size[0]/2, size[1]/2-h]], numpy.float32))
	
	return ret