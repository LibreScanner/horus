# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.\
                 Copyright (C) 2013 David Braam from Cura Project'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import os
import urllib2
import webbrowser

from horus.util import resources, system as sys


def getVersion(_type='local'):
    return _getVersionData(0, _type)


def getBuild(_type='local'):
    return _getVersionData(1, _type)


def getGitHub(_type='local'):
    return _getVersionData(2, _type)


def _getVersionData(index, _type='local'):
    # Version Build GitHub
    try:
        if _type is 'local':
            if os.path.isfile(resources.getPathForVersion()):
                with open(resources.getPathForVersion(), 'r') as f:
                    content = f.read()
        elif _type is 'remote':
            f = urllib2.urlopen('http://storage.googleapis.com/bq-horus/releases/version')
            content = f.read()
        data = content.split('\n')
        return data[index]
    except:
        return ''


def checkForUpdates():
    return getVersion('remote') >= getVersion('local') and \
        getBuild('local') is not '' and \
        getBuild('remote') > getBuild('local')


def _getExecutableUrl(version):
    url = None
    import platform
    if sys.isLinux():
        url = "https://launchpad.net/~bqopensource/+archive/ubuntu/horus/+files/"
        url += "horus_"
        url += version + "-bq1~"
        url += platform.linux_distribution()[2] + "1_"
        if platform.architecture()[0] == '64bit':
            url += "amd64.deb"
        elif platform.architecture()[0] == '32bit':
            url += "i386.deb"
    elif sys.isWindows():
        url = "storage.googleapis.com/bq-horus/releases/"
        url += "Horus_"
        url += version + ".exe"
    elif sys.isDarwin():
        url = "https://storage.googleapis.com/bq-horus/releases/"
        url += "Horus_"
        url += version + ".dmg"
    del platform
    return url


def _downloadVersion(version):
    url = _getExecutableUrl(version)
    if url is not None:
        webbrowser.open(url)


def downloadLatestVersion():
    _downloadVersion(getVersion('remote'))
