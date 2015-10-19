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


def get_version(_type='local'):
    return _get_version_data(0, _type)


def get_build(_type='local'):
    return _get_version_data(1, _type)


def get_github(_type='local'):
    return _get_version_data(2, _type)


def _get_version_data(index, _type='local'):
    # Version Build GitHub
    try:
        if _type is 'local':
            version_file = resources.get_path_for_version()
            if os.path.isfile(version_file):
                with open(version_file, 'r') as f:
                    content = f.read()
        elif _type is 'remote':
            # TODO: save file
            f = urllib2.urlopen('http://storage.googleapis.com/bq-horus/releases/version')
            content = f.read()
        data = content.split('\n')
        return data[index]
    except:
        return ''


def check_for_updates():
    return get_version('remote') >= get_version('local') and \
        get_build('local') is not '' and \
        get_build('remote') > get_build('local')


def _get_executable_url(version):
    url = None
    if sys.is_linux():
        import platform
        url = "https://launchpad.net/~bqopensource/+archive/ubuntu/horus/+files/"
        url += "horus_"
        url += version + "-bq1~"
        url += platform.linux_distribution()[2] + "1_"
        if platform.architecture()[0] == '64bit':
            url += "amd64.deb"
        elif platform.architecture()[0] == '32bit':
            url += "i386.deb"
        del platform
    elif sys.is_windows():
        url = "storage.googleapis.com/bq-horus/releases/"
        url += "Horus_"
        url += version + ".exe"
    elif sys.is_darwin():
        url = "https://storage.googleapis.com/bq-horus/releases/"
        url += "Horus_"
        url += version + ".dmg"
    return url


def _download_version(version):
    url = _get_executable_url(version)
    if url is not None:
        webbrowser.open(url)


def download_latest_version():
    _download_version(get_version('remote'))
