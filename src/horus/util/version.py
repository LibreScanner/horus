# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.\
                 Copyright (C) 2013 David Braam from Cura Project'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import json
import urllib2
import webbrowser

from horus import __version__, __datetime__, __commit__
from horus.util import system as sys

current_version = __version__
current_datetime = __datetime__
current_commit = __commit__

latest_version = ''
latest_datetime = ''
latest_commit = ''

URL_API_RELEASES = 'https://api.github.com/repos/bqlabs/horus/releases/latest'
URL_DOWNLOAD = 'https://github.com/bqlabs/horus/releases/download/'

try:
    f = urllib2.urlopen(URL_API_RELEASES, timeout=1)
    content = json.loads(f.read())
    tag_name = content['tag_name']
    f = urllib2.urlopen(URL_DOWNLOAD + tag_name + '/version', timeout=1)
    content = json.loads(f.read())
    latest_version = content['version']
    latest_datetime = content['datetime']
    latest_commit = content['commit']
except:
    pass


def check_for_updates():
    return latest_version >= current_version and \
        current_datetime is not '' and \
        latest_datetime > current_datetime


def _get_executable_url(version):
    url = None
    if sys.is_linux():
        import platform
        url = 'https://launchpad.net/~bqlabs/+archive/ubuntu/horus/+files/'
        url += 'horus_'
        url += version + '-'
        url += platform.linux_distribution()[2] + '1_'
        if platform.architecture()[0] == '64bit':
            url += 'amd64.deb'
        elif platform.architecture()[0] == '32bit':
            url += 'i386.deb'
        del platform
    elif sys.is_windows():
        url = URL_DOWNLOAD
        url += 'Horus_'
        url += version + '.exe'
    elif sys.is_darwin():
        url = URL_DOWNLOAD
        url += 'Horus_'
        url += version + '.dmg'
    return url


def download_latest_version():
    url = _get_executable_url(latest_version)
    if url is not None:
        webbrowser.open(url)
