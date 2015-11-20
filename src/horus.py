# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


try:
    import os
    import wx
    import cv2
    import OpenGL
    import serial
    import numpy
    import scipy
    import matplotlib
except ImportError as e:
    print e.message
    exit(1)

from horus.util import resources
resources.set_base_path(os.path.join(os.path.dirname(__file__), "../res"))

from horus.gui import app


def main():
    app.HorusApp().MainLoop()

if __name__ == '__main__':
    main()
