# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>\
              Nicanor Romero Venier <nicanor.romerovenier@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.\
                 Copyright (C) 2013 David Braam from Cura Project'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import os
import math
import sys
import collections
import json
import types
import numpy as np

if sys.version_info[0] < 3:
    import ConfigParser
else:
    import configparser as ConfigParser

from horus.util import resources, system


class Settings(collections.MutableMapping):

    def __init__(self):
        self._settings_dict = dict()
        self.settings_version = 1

    # Getters

    def __getitem__(self, key):
        # For convinience, this returns the Setting value and not the Setting object itself
        if self._settings_dict[key].value is not None:
            return self._settings_dict[key].value
        else:
            return self._settings_dict[key].default

    def getSetting(self, key):
        return self._settings_dict[key]

    def getLabel(self, key):
        return self.getSetting(key)._label

    def getDefault(self, key):
        return self.getSetting(key).default

    def getMinValue(self, key):
        return self.getSetting(key).min_value

    def getMaxValue(self, key):
        return self.getSetting(key).max_value

    def getPossibleValues(self, key):
        return self.getSetting(key)._possible_values

    # Setters

    def __setitem__(self, key, value):
        # For convinience, this sets the Setting value and not a Setting object
        self.getSetting(key).value = value

    def setMinValue(self, key, value):
        self.getSetting(key).__min_value = value

    def setMaxValue(self, key, value):
        self.getSetting(key).__max_value = value

    def castAndSet(self, key, value):
        if len(value) == 0:
            return
        setting_type = self.getSetting(key)._type
        try:
            if setting_type == types.BooleanType:
                value = bool(value)
            elif setting_type == types.IntType:
                value = int(value)
            elif setting_type == types.FloatType:
                value = float(value)
            elif setting_type == types.UnicodeType:
                value = unicode(value)
            elif setting_type == types.ListType:
                from ast import literal_eval
                value = literal_eval(value)
            elif setting_type == np.ndarray:
                from ast import literal_eval
                value = np.asarray(literal_eval(value))
        except:
            raise ValueError("Unable to cast setting %s to type %s" % (key, setting_type))
        else:
            self.__setitem__(key, value)

    # File management

    def loadSettings(self, filepath=None, categories=None):
        if filepath is None:
            filepath = os.path.join(getBasePath(), 'settings.json')
        with open(filepath, 'r') as f:
            self._loadJsonDict(json.loads(f.read()), categories)

    def _loadJsonDict(self, json_dict, categories):
        for category in json_dict.keys():
            if category == "settings_version":
                continue
            if categories is None or category in categories:
                for key in json_dict[category]:
                    if key in self._settings_dict:
                        self._convertToType(key, json_dict[category][key])
                        self.getSetting(key)._loadJsonDict(json_dict[category][key])

    def _convertToType(self, key, json_dict):
        if self._settings_dict[key]._type == np.ndarray:
            json_dict['value'] = np.asarray(json_dict['value'])

    def saveSettings(self, filepath=None, categories=None):
        if filepath is None:
            filepath = os.path.join(getBasePath(), 'settings.json')

        # If trying to overwrite some categories of settings.json, first load it
        # to preserve the other values
        if categories is not None and filepath == os.path.join(getBasePath(), 'settings.json'):
            with open(filepath, 'r') as f:
                initial_json = json.loads(f.read())
        else:
            initial_json = None

        with open(filepath, 'w') as f:
            f.write(
                json.dumps(self._toJsonDict(categories, initial_json), sort_keys=True, indent=4))

    def _toJsonDict(self, categories, initial_json=None):
        if initial_json is None:
            json_dict = dict()
        else:
            json_dict = initial_json.copy()

        json_dict["settings_version"] = self.settings_version
        for key in self._settings_dict.keys():
            if categories is not None and self.getSetting(key)._category not in categories:
                continue
            if self.getSetting(key)._category not in json_dict:
                json_dict[self.getSetting(key)._category] = dict()
            json_dict[self.getSetting(key)._category][key] = self.getSetting(key)._toJsonDict()
        return json_dict

    # Other

    def __delitem__(self, key):
        del self._settings_dict[key]

    def __iter__(self):
        return iter(self._settings_dict)

    def __len__(self):
        return len(self._settings_dict)

    def resetToDefault(self, key=None, categories=None):
        if key is not None:
            self.__setitem__(key, self.getSetting(key).default)
        else:
            for key in self._settings_dict.keys():
                if categories is not None and self.getSetting(key)._category not in categories:
                    continue
                self.__setitem__(key, self.getSetting(key).default)

    def _addSetting(self, setting):
        self._settings_dict[setting._id] = setting

    def _initializeSettings(self):

        # -- Scan Settings

        # Hack to translate combo boxes:
        _('High')
        _('Medium')
        _('Low')
        self._addSetting(
            Setting('luminosity', _('Luminosity'), 'scan_settings',
                    unicode, u'Medium', possible_values=(u'High', u'Medium', u'Low')))
        self._addSetting(
            Setting('brightness_control', _('Brightness'), 'scan_settings',
                    int, 128, min_value=0, max_value=255))
        self._addSetting(
            Setting('contrast_control', _('Contrast'), 'scan_settings',
                    int, 32, min_value=0, max_value=255))
        self._addSetting(
            Setting('saturation_control', _('Saturation'), 'scan_settings',
                    int, 32, min_value=0, max_value=255))
        self._addSetting(
            Setting('exposure_control', _('Exposure'), 'scan_settings',
                    int, 16, min_value=1, max_value=512))
        self._addSetting(
            Setting('framerate', _('Framerate'), 'scan_settings',
                    int, 30, possible_values=(30, 25, 20, 15, 10, 5)))
        self._addSetting(
            Setting('resolution', _('Resolution'), 'scan_settings',
                    unicode, u'1280x960', possible_values=(u'1280x960',
                                                           u'960x720',
                                                           u'800x600',
                                                           u'320x240',
                                                           u'160x120')))
        self._addSetting(
            Setting('use_distortion', _('Use distortion'), 'scan_settings', bool, False))

        self._addSetting(
            Setting('motor_step_control', _(u'Step (º)'), 'scan_settings',
                    float, 90.0))
        self._addSetting(
            Setting('motor_speed_control', _(u'Speed (º/s)'), 'scan_settings',
                    float, 200.0, min_value=1.0, max_value=1000.0))
        self._addSetting(
            Setting('motor_acceleration_control', _(u'Acceleration (º/s²)'), 'scan_settings',
                    float, 200.0, min_value=1.0, max_value=1000.0))

        # Hack to translate combo boxes:
        _('Texture')
        _('Laser')
        self._addSetting(
            Setting('capture_mode_scanning', _('Capture mode'), 'scan_settings',
                    unicode, u'Texture', possible_values=(u'Texture', u'Laser')))

        self._addSetting(
            Setting('brightness_texture_scanning', _('Brightness'), 'scan_settings',
                    int, 100, min_value=0, max_value=255))
        self._addSetting(
            Setting('contrast_texture_scanning', _('Contrast'), 'scan_settings',
                    int, 32, min_value=0, max_value=255))
        self._addSetting(
            Setting('saturation_texture_scanning', _('Saturation'), 'scan_settings',
                    int, 100, min_value=0, max_value=255))
        self._addSetting(
            Setting('exposure_texture_scanning', _('Exposure'), 'scan_settings',
                    int, 16, min_value=1, max_value=512))

        self._addSetting(
            Setting('brightness_laser_scanning', _('Brightness'), 'scan_settings',
                    int, 100, min_value=0, max_value=255))
        self._addSetting(
            Setting('contrast_laser_scanning', _('Contrast'), 'scan_settings',
                    int, 20, min_value=0, max_value=255))
        self._addSetting(
            Setting('saturation_laser_scanning', _('Saturation'), 'scan_settings',
                    int, 60, min_value=0, max_value=255))
        self._addSetting(
            Setting('exposure_laser_scanning', _('Exposure'), 'scan_settings',
                    int, 6, min_value=1, max_value=512))
        self._addSetting(
            Setting('remove_background_scanning', _('Remove background'),
                    'scan_settings', bool, True))

        self._addSetting(
            Setting('red_channel_scanning', _('Red channel'), 'scan_settings',
                    unicode, u'R (RGB)', possible_values=(u'R (RGB)', u'Cr (YCrCb)', u'U (YUV)')))
        self._addSetting(
            Setting('open_enable_scanning', _('Enable open'), 'scan_settings', bool, True))
        self._addSetting(
            Setting('open_value_scanning', _('Open value'), 'scan_settings',
                    int, 2, min_value=1, max_value=10))
        self._addSetting(
            Setting('threshold_enable_scanning', _('Enable threshold'),
                    'scan_settings', bool, True))
        self._addSetting(
            Setting('threshold_value_scanning', _('Threshold value'), 'scan_settings',
                    int, 6, min_value=0, max_value=255))

        # Hack to translate combo boxes:
        _('Pattern')
        _('Laser')
        self._addSetting(
            Setting('capture_mode_calibration', _('Capture mode'), 'scan_settings',
                    unicode, u'Pattern', possible_values=(u'Pattern', u'Laser')))

        self._addSetting(
            Setting('brightness_pattern_calibration', _('Brightness'), 'scan_settings',
                    int, 100, min_value=0, max_value=255))
        self._addSetting(
            Setting('contrast_pattern_calibration', _('Contrast'), 'scan_settings',
                    int, 32, min_value=0, max_value=255))
        self._addSetting(
            Setting('saturation_pattern_calibration', _('Saturation'), 'scan_settings',
                    int, 100, min_value=0, max_value=255))
        self._addSetting(
            Setting('exposure_pattern_calibration', _('Exposure'), 'scan_settings',
                    int, 16, min_value=1, max_value=512))

        self._addSetting(
            Setting('brightness_laser_calibration', _('Brightness'), 'scan_settings',
                    int, 100, min_value=0, max_value=255))
        self._addSetting(
            Setting('contrast_laser_calibration', _('Contrast'), 'scan_settings',
                    int, 20, min_value=0, max_value=255))
        self._addSetting(
            Setting('saturation_laser_calibration', _('Saturation'), 'scan_settings',
                    int, 60, min_value=0, max_value=255))
        self._addSetting(
            Setting('exposure_laser_calibration', _('Exposure'), 'scan_settings',
                    int, 6, min_value=1, max_value=512))
        self._addSetting(
            Setting('remove_background_calibration', _('Remove background'),
                    'scan_settings', bool, True))

        self._addSetting(
            Setting('red_channel_calibration', _('Red channel'), 'scan_settings',
                    unicode, u'R (RGB)', possible_values=(u'R (RGB)', u'Cr (YCrCb)', u'U (YUV)')))
        self._addSetting(
            Setting('open_enable_calibration', _('Enable open'), 'scan_settings', bool, True))
        self._addSetting(
            Setting('open_value_calibration', _('Open value'), 'scan_settings',
                    int, 2, min_value=1, max_value=10))
        self._addSetting(
            Setting('threshold_enable_calibration', _('Enable threshold'),
                    'scan_settings', bool, True))
        self._addSetting(
            Setting('threshold_value_calibration', _('Threshold value'), 'scan_settings',
                    int, 6, min_value=0, max_value=255))

        self._addSetting(
            Setting('capture_texture', _('Capture texture'), 'scan_settings', bool, True))
        # Hack to translate combo boxes:
        _('Left')
        _('Right')
        _('Both')
        self._addSetting(
            Setting('use_laser', _('Use laser'), 'scan_settings',
                    unicode, u'Both', possible_values=(u'Left', u'Right', u'Both')))

        self._addSetting(
            Setting('motor_step_scanning', _(u'Step (º)'), 'scan_settings',
                    float, 0.45))
        self._addSetting(
            Setting('motor_speed_scanning', _(u'Speed (º/s)'), 'scan_settings',
                    float, 200.0, min_value=1.0, max_value=1000.0))
        self._addSetting(
            Setting('motor_acceleration_scanning', _(u'Acceleration (º/s²)'), 'scan_settings',
                    float, 300.0, min_value=1.0, max_value=1000.0))

        self._addSetting(
            Setting('point_cloud_color', _('Choose Point Cloud Color'), 'scan_settings',
                    unicode, u'AAAAAA'))

        # Hack to translate combo boxes:
        _('Texture')
        _('Laser')
        _('Gray')
        _('Line')
        self._addSetting(
            Setting('video_scanning', _('Video'), 'scan_settings',
                    unicode, u'Laser', possible_values=(u'Texture', u'Laser', u'Gray', u'Line')))

        self._addSetting(Setting('left_button', _('Left'), 'scan_settings', unicode, u''))
        self._addSetting(Setting('right_button', _('Right'), 'scan_settings', unicode, u''))
        self._addSetting(Setting('move_button', _('Move'), 'scan_settings', unicode, u''))
        self._addSetting(Setting('enable_button', _('Enable'), 'scan_settings', unicode, u''))
        self._addSetting(Setting('gcode_gui', _('Send'), 'scan_settings', unicode, u''))
        self._addSetting(Setting('ldr_value', _('Send'), 'scan_settings', unicode, u''))
        self._addSetting(
            Setting('autocheck_button', _('Perform autocheck'), 'scan_settings', unicode, u''))

        # -- Calibration Settings

        self._addSetting(
            Setting('pattern_rows', _('Pattern rows'), 'calibration_settings',
                    int, 6, min_value=2, max_value=50))
        self._addSetting(
            Setting('pattern_columns', _('Pattern columns'), 'calibration_settings',
                    int, 11, min_value=2, max_value=50))
        self._addSetting(
            Setting('pattern_square_width', _('Square width (mm)'), 'calibration_settings',
                    float, 13.0, min_value=1.0))
        self._addSetting(
            Setting('pattern_origin_distance', _('Origin distance (mm)'), 'calibration_settings',
                    float, 0.0, min_value=0.0))

        self._addSetting(
            Setting('adjust_laser', _('Adjust Laser'), 'calibration_settings', bool, True))

        self._addSetting(
            Setting('camera_matrix', _('Camera matrix'), 'calibration_settings',
                    np.ndarray, np.ndarray(shape=(3, 3), buffer=np.array([[1430.0, 0.0, 480.0],
                                                                          [0.0, 1430.0, 640.0],
                                                                          [0.0, 0.0, 1.0]]))))
        self._addSetting(
            Setting('distortion_vector', _('Distortion vector'), 'calibration_settings',
                    np.ndarray, np.ndarray(shape=(5,),
                                           buffer=np.array([0.0, 0.0, 0.0, 0.0, 0.0]))))

        self._addSetting(
            Setting('distance_left', _('Distance'), 'calibration_settings', float, 0.0))
        self._addSetting(
            Setting('normal_left', _('Normal'), 'calibration_settings',
                    np.ndarray, np.ndarray(shape=(3,), buffer=np.array([0.0, 0.0, 0.0]))))
        self._addSetting(
            Setting('distance_right', _('Distance'), 'calibration_settings', float, 0.0))
        self._addSetting(
            Setting('normal_right', _('Normal'), 'calibration_settings',
                    np.ndarray, np.ndarray(shape=(3,), buffer=np.array([0.0, 0.0, 0.0]))))

        self._addSetting(
            Setting('rotation_matrix', _('Rotation matrix'), 'calibration_settings',
                    np.ndarray, np.ndarray(shape=(3, 3), buffer=np.array([[0.0, 1.0, 0.0],
                                                                          [0.0, 0.0, -1.0],
                                                                          [-1.0, 0.0, 0.0]]))))
        self._addSetting(
            Setting('translation_vector', _('Translation vector'), 'calibration_settings',
                    np.ndarray, np.ndarray(shape=(3,), buffer=np.array([5.0, 80.0, 320.0]))))

        # -- Machine Settings

        self._addSetting(
            Setting('machine_diameter', _('Machine Diameter'), 'machine_settings', int, 200))
        self._addSetting(
            Setting('machine_width', _('Machine Width'), 'machine_settings', int, 200))
        self._addSetting(
            Setting('machine_height', _('Machine Height'), 'machine_settings', int, 200))
        self._addSetting(
            Setting('machine_depth', _('Machine Depth'), 'machine_settings', int, 200))
        # Hack to translate combo boxes:
        _('Circular')
        _('Rectangular')
        self._addSetting(
            Setting('machine_shape', _('Machine Shape'), 'machine_settings',
                    unicode, u'Circular', possible_values=(u'Circular', u'Rectangular')))
        self._addSetting(
            Setting('machine_model_path', _('Machine Model'), 'machine_settings',
                    unicode, unicode(resources.getPathForMesh('ciclop_platform.stl'))))
        self._addSetting(
            Setting('roi_view', _('View ROI'), 'machine_settings', bool, False))
        self._addSetting(
            Setting('roi_diameter', _('Diameter (mm)'), 'machine_settings',
                    int, 200, min_value=0, max_value=250))
        self._addSetting(
            Setting('roi_width', _('Width (mm)'), 'machine_settings',
                    int, 200, min_value=0, max_value=250))
        self._addSetting(
            Setting('roi_height', _('Height (mm)'), 'machine_settings',
                    int, 200, min_value=0, max_value=250))
        self._addSetting(
            Setting('roi_depth', _('Depth (mm)'), 'machine_settings',
                    int, 200, min_value=0, max_value=250))

        # -- Preferences

        self._addSetting(
            Setting('serial_name', _('Serial Name'), 'preferences', unicode, u'/dev/ttyUSB0'))
        self._addSetting(
            Setting('baud_rate', _('Baud rate'), 'preferences', int, 115200,
                    possible_values=(9600, 14400, 19200, 38400, 57600, 115200)))
        self._addSetting(
            Setting('camera_id', _('Camera Id'), 'preferences', unicode, u'/dev/video0'))
        self._addSetting(
            Setting('board', _('Board'), 'preferences', unicode, u'BT ATmega328',
                    possible_values=(u'Arduino Uno', u'BT ATmega328')))
        self._addSetting(
            Setting('invert_motor', _('Invert motor'), 'preferences', bool, False))
        self._addSetting(
            Setting('language', _('Language'), 'preferences', unicode, u'English',
                    possible_values=(u'English', u'Español', u'Français',
                                     u'Deutsch', u'Italiano', u'Português'),
                    tooltip=_('Change the language in which Horus runs. '
                              'Switching language requires a restart of Horus')))

        # Hack to translate combo boxes:
        _('Control workbench')
        _('Adjustment workbench')
        _('Calibration workbench')
        _('Scanning workbench')
        self._addSetting(
            Setting('workbench', _('Workbench'), 'preferences', unicode, u'Scanning workbench',
                    possible_values=(u'Control workbench',
                                     u'Adjustment workbench',
                                     u'Calibration workbench',
                                     u'Scanning workbench')))
        self._addSetting(
            Setting('show_welcome', _('Show Welcome'), 'preferences', bool, True))
        self._addSetting(
            Setting('check_for_updates', _('Check for Updates'), 'preferences', bool, True))
        self._addSetting(
            Setting('basic_mode', _('Basic Mode'), 'preferences', bool, False))
        self._addSetting(
            Setting('view_control_panel', _('View Control Panel'), 'preferences', bool, True))
        self._addSetting(
            Setting('view_control_video', _('View Control Panel'), 'preferences', bool, True))
        self._addSetting(
            Setting('view_adjustment_panel', _('View Adjustment Panel'),
                    'preferences', bool, True))
        self._addSetting(
            Setting('view_adjustment_video', _('View Adjustment Video'),
                    'preferences', bool, True))
        self._addSetting(
            Setting('view_calibration_panel', _('View Calibration Panel'),
                    'preferences', bool, True))
        self._addSetting(
            Setting('view_calibration_video', _('View Calibration Video'),
                    'preferences', bool, True))
        self._addSetting(
            Setting('view_scanning_panel', _('View Scanning Panel'), 'preferences', bool, False))
        self._addSetting(
            Setting('view_scanning_video', _('View Scanning Video'), 'preferences', bool, False))
        self._addSetting(
            Setting('view_scanning_scene', _('View Scanning Scene'), 'preferences', bool, True))

        self._addSetting(
            Setting('last_files', _('Last Files'), 'preferences', list, []))
        # TODO: Set this default value
        self._addSetting(
            Setting('last_file', _('Last File'), 'preferences', unicode, u''))
        # TODO: Set this default value
        self._addSetting(
            Setting('last_profile', _('Last Profile'), 'preferences', unicode, u''))


class Setting(object):

    def __init__(self, setting_id, label, category, setting_type, default,
                 min_value=None, max_value=None, possible_values=None, tooltip='', tag=None):
        self._id = setting_id
        self._label = label
        self._category = category
        self._type = setting_type
        self._tooltip = tooltip
        self._tag = tag

        self.min_value = min_value
        self.max_value = max_value
        self._possible_values = possible_values
        self.default = default
        self.__value = None

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value is None:
            return
        self._checkType(value)
        self._checkRange(value)
        self._checkPossibleValues(value)
        self.__value = value

    @property
    def default(self):
        return self.__default

    @default.setter
    def default(self, value):
        self._checkType(value)
        self._checkRange(value)
        self._checkPossibleValues(value)
        self.__default = value

    @property
    def min_value(self):
        return self.__min_value

    @min_value.setter
    def min_value(self, value):
        if value is not None:
            self._checkType(value)
        self.__min_value = value

    @property
    def max_value(self):
        return self.__max_value

    @max_value.setter
    def max_value(self, value):
        if value is not None:
            self._checkType(value)
        self.__max_value = value

    def _checkType(self, value):
        if not isinstance(value, self._type):
            raise TypeError("Error when setting %s.\n%s (%s) is not of type %s." %
                            (self._id, value, type(value), self._type))

    def _checkRange(self, value):
        if self.min_value is not None and value < self.min_value:
            # raise ValueError('Error when setting %s.\n%s is below min value %s.' %
            # (self._id, value, self.min_value))
            print 'Warning: For setting %s, %s is below min value %s.' % \
                (self._id, value, self.min_value)
        if self.max_value is not None and value > self.max_value:
            # raise ValueError('Error when setting %s.\n%s is above max value %s.' %
            # (self._id, value, self.max_value))
            print 'Warning: For setting %s.\n%s is above max value %s.' % \
                (self._id, value, self.max_value)

    def _checkPossibleValues(self, value):
        if self._possible_values is not None and value not in self._possible_values:
            raise ValueError('Error when setting %s.\n%s is not within the possible values %s.' % (
                self._id, value, self._possible_values))

    def _loadJsonDict(self, json_dict):
        # Only load configurable fields (__value, __min_value, __max_value)
        self.value = json_dict['value']
        self.min_value = json_dict['min_value']
        self.max_value = json_dict['max_value']

    def _toJsonDict(self):
        # Convert only configurable fields
        json_dict = dict()

        if self.value is None:
            value = self.default
        else:
            value = self.value

        if self._type == np.ndarray and value is not None:
            json_dict['value'] = value.tolist()
        else:
            json_dict['value'] = value

        json_dict['min_value'] = self.min_value
        json_dict['max_value'] = self.max_value
        return json_dict


# Define a fake _() function to fake the gettext tools in to generating
# strings for the profile settings.

def _(n):
    return n

settings = Settings()
settings._initializeSettings()

# Remove fake defined _() because later the localization will define a global _()
del _


def getBasePath():
    """
    :return: The path in which the current configuration files are stored.
    This depends on the used OS.
    """
    if system.isWindows():
        basePath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        # If we have a frozen python install, we need to step out of the library.zip
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


# Temporary function to migrate old settings (INI) into new ones (JSON)
def loadSettings():
    if os.path.exists(os.path.join(getBasePath(), 'settings.json')):
        settings.loadSettings()
        return
    else:
        for setting_file in ('machine_settings.ini', 'current-profile.ini', 'preferences.ini'):
            try:
                loadOldSettings(os.path.join(getBasePath(), setting_file))
            except:
                pass  # Setting file might not exist
        settings.saveSettings()

# Temporary function to migrate old settings (INI) into new ones (JSON)


def loadOldSettings(filename):
    profileParser = ConfigParser.ConfigParser()
    try:
        profileParser.read(filename)
    except ConfigParser.ParsingError:
        print "Unable to read file: %s" % filename
    section = profileParser.sections()[0]

    for key in settings:
        if profileParser.has_option(section, key):
            setting_type = settings.getSetting(key)._type
            if setting_type == types.BooleanType:
                settings[key] = bool(profileParser.get(section, key))
            elif setting_type == types.IntType:
                settings[key] = int(float(profileParser.get(section, key)))
            elif setting_type == types.FloatType:
                settings[key] = float(profileParser.get(section, key))
            elif setting_type == types.UnicodeType:
                settings[key] = unicode(profileParser.get(section, key))
            elif setting_type == types.ListType:
                from ast import literal_eval
                settings[key] = literal_eval(profileParser.get(section, key))
            elif setting_type == np.ndarray:
                from ast import literal_eval
                settings[key] = np.asarray(literal_eval(profileParser.get(section, key)))
            else:
                raise TypeError(
                    "Unknown type when loading old setting %s of type %s" % (key, setting_type))


# TODO: Move these somewhere else

# Returns a list of convex polygons, first polygon is the allowed area of the machine,
# the rest of the polygons are the dis-allowed areas of the machine.
def getMachineSizePolygons(machine_shape):
    if machine_shape == "Circular":
        size = np.array(
            [settings['machine_diameter'],
             settings['machine_diameter'],
             settings['machine_height']], np.float32)
    elif machine_shape == "Rectangular":
        size = np.array([settings['machine_width'],
                         settings['machine_depth'],
                         settings['machine_height']], np.float32)
    return getSizePolygons(size, machine_shape)


def getSizePolygons(size, machine_shape):
    ret = []
    if machine_shape == 'Circular':
        circle = []
        steps = 32
        for n in xrange(0, steps):
            circle.append([math.cos(float(n) / steps * 2 * math.pi) * size[0] / 2,
                           math.sin(float(n) / steps * 2 * math.pi) * size[1] / 2])
        ret.append(np.array(circle, np.float32))

    elif machine_shape == 'Rectangular':
        rectangle = []
        rectangle.append([-size[0] / 2, size[1] / 2])
        rectangle.append([size[0] / 2, size[1] / 2])
        rectangle.append([size[0] / 2, -size[1] / 2])
        rectangle.append([-size[0] / 2, -size[1] / 2])
        ret.append(np.array(rectangle, np.float32))

    w = 20
    h = 20
    ret.append(np.array([[-size[0] / 2, -size[1] / 2],
                         [-size[0] / 2 + w + 2, -size[1] / 2],
                         [-size[0] / 2 + w, -size[1] / 2 + h],
                         [-size[0] / 2, -size[1] / 2 + h]], np.float32))
    ret.append(np.array([[size[0] / 2 - w - 2, -size[1] / 2],
                         [size[0] / 2, -size[1] / 2],
                         [size[0] / 2, -size[1] / 2 + h],
                         [size[0] / 2 - w, -size[1] / 2 + h]], np.float32))
    ret.append(np.array([[-size[0] / 2 + w + 2, size[1] / 2],
                         [-size[0] / 2, size[1] / 2],
                         [-size[0] / 2, size[1] / 2 - h],
                         [-size[0] / 2 + w, size[1] / 2 - h]], np.float32))
    ret.append(np.array([[size[0] / 2, size[1] / 2],
                         [size[0] / 2 - w - 2, size[1] / 2],
                         [size[0] / 2 - w, size[1] / 2 - h],
                         [size[0] / 2, size[1] / 2 - h]], np.float32))

    return ret
