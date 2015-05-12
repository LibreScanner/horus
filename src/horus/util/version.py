#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014-2015 Mundo Reader S.L.                             #
# Copyright (C) 2013 David Braam from Cura Project                      #
#                                                                       #
# Date: May 2015                                                        #
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
import urllib2
import webbrowser

from horus.util import resources

def getVersion(_type='local'):
    return _getVersionData(0, _type)

def getBuild(_type='local'):
    return _getVersionData(1, _type)

def getGitHub(_type='local'):
    return _getVersionData(2, _type)

def _getVersionData(index, _type='local'):
    ## Version Build GitHub
    try:
        if _type is 'local':
            if os.path.isfile(resources.getPathForVersion()):
                with open(resources.getPathForVersion(), 'r') as f:
                    content = f.read()
        elif _type is 'remote':
            #f = urllib2.urlopen('storage.googleapis.com/bq-horus/releases/version')
            f = urllib2.urlopen('http://127.0.0.1:3000/version')
            content = f.read()
        data = content.split('\n')
        return data[index]
    except:
        return ''

def checkForUpdates():
    return getVersion('remote') >= getVersion('local') and \
           getBuild('remote') > getBuild('local')

def _getExecutableUrl(version):
    url = None
    import platform
    if platform.system() == 'Linux':
        url = "https://launchpad.net/~bqopensource/+archive/ubuntu/horus/+files/"
        url += "horus_"
        url += version+"-bq1~"
        url += platform.linux_distribution()[2]+"1_"
        if platform.architecture()[0] == '64bit':
            url += "amd64.deb"
        elif platform.architecture()[0] == '32bit':
            url += "i386.deb"
    elif platform.system() == 'Windows':
        url = "storage.googleapis.com/bq-horus/releases/"
        url += "Horus_"
        url += version+".exe"
    del platform
    return url

def _downloadVersion(version):
    url = _getExecutableUrl(version)
    if url is not None:
        webbrowser.open(url)

def downloadLastestVersion():
    _downloadVersion(getVersion('remote'))