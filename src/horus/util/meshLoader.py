# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.\
                 Copyright (C) 2013 David Braam from Cura Project'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import os

from horus.util.meshLoaders import ply
from horus.util.meshLoaders import stl


def loadSupportedExtensions():
    """ return a list of supported file extensions for loading. """
    return ['.ply', '.stl']


def saveSupportedExtensions():
    """ return a list of supported file extensions for saving. """
    return ['.ply']


def loadMesh(filename):
    """
    loadMesh loads one model from a file.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.ply':
        return ply.loadScene(filename)
    if ext == '.stl':
        return stl.loadScene(filename)
    print 'Error: Unknown model extension: %s' % (ext)
    return None


def saveMesh(filename, _object):
    """
    Save a object into the file given by the filename.
    Use the filename extension to find out the file format.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.ply':
        ply.saveScene(filename, _object)
        return
    print 'Error: Unknown model extension: %s' % (ext)
