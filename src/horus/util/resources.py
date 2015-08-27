# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.\
                 Copyright (C) 2013 David Braam from Cura Project'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import os
import sys
import glob
import gettext

from horus.util import system

resourceBasePath = ''


def setBasePath(path):
    global resourceBasePath
    resourceBasePath = path


def getPathForResource(dir, subdir, resource_name):
    assert os.path.isdir(dir), "{p} is not a directory".format(p=dir)
    path = os.path.normpath(os.path.join(dir, subdir, resource_name))
    return path


def getPathForVersion(name='version'):
    return getPathForResource(resourceBasePath, '.', name)


def getPathForImage(name):
    return getPathForResource(resourceBasePath, 'images', name)


def getPathForFirmware(name):
    return getPathForResource(resourceBasePath, 'firmware', name)


def getPathForTools(name):
    if system.isWindows():
        path = getPathForResource(resourceBasePath, 'tools/windows', name)
    elif system.isDarwin():
        path = getPathForResource(resourceBasePath, 'tools/darwin', name)
    else:
        path = getPathForResource(resourceBasePath, 'tools/linux', name)
    return path


def getPathForMesh(name):
    return getPathForResource(resourceBasePath, 'meshes', name)

"""def getDefaultMachineProfiles():
    path = os.path.normpath(os.path.join(resourceBasePath, 'machine_profiles', '*.ini'))
    return glob.glob(path)"""


def setupLocalization(selectedLanguage=None):
    # Default to english
    languages = ['en']

    if selectedLanguage is not None:
        for item in getLanguageOptions():
            if item[1] == selectedLanguage and item[0] is not None:
                languages = [item[0]]

    locale_path = os.path.normpath(os.path.join(resourceBasePath, 'locale'))
    translation = gettext.translation('horus', locale_path, languages, fallback=True)
    translation.install(unicode=True)


def getLanguageOptions():
    return [
        ['en', u'English'],
        ['es', u'Español'],
        ['fr', u'Français'],
        ['de', u'Deutsch'],
        ['it', u'Italiano'],
        ['pt', u'Português'],
    ]
