#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


# Check dependencies
try:
    import os
    import wx
    import sys
    import cv2
    import OpenGL
    import serial
    import numpy
    import scipy
    import matplotlib
except ImportError as e:
    print(e.message)
    exit(1)

# Try first the sources
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from horus.util import resources

resdir = os.path.join(os.path.dirname(__file__), "res")
if not os.path.exists(resdir):
    resdir = "/usr/share/horus"

resources.set_base_path(resdir)


def main():
    from horus.gui import app
    app.HorusApp().MainLoop()

if __name__ == '__main__':
    main()
