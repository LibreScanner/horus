# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


class ScanCapture(object):

    def __init__(self):
        self.theta = 0
        self.color = (0, 0, 0)
        self.img_texture = None
        self.img_no_laser = None
        self.img_laser = [None, None]
