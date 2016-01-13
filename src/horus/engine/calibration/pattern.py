# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import numpy as np

from horus import Singleton


@Singleton
class Pattern(object):

    def __init__(self):
        self._rows = 0
        self._columns = 0
        self._square_width = 0
        self.origin_distance = 0

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value):
        value = self.to_int(value)
        if self._rows != value:
            self._rows = value
            self._generate_object_points()

    def set_rows(self, value):
        self.rows = value

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        value = self.to_int(value)
        if self._columns != value:
            self._columns = value
            self._generate_object_points()

    def set_columns(self, value):
        self.columns = value

    @property
    def square_width(self):
        return self._square_width

    @square_width.setter
    def square_width(self, value):
        value = self.to_float(value)
        if self._square_width != value:
            self._square_width = value
            self._generate_object_points()

    def set_square_width(self, value):
        self.square_width = value

    def _generate_object_points(self):
        objp = np.zeros((self.rows * self.columns, 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.columns, 0:self.rows].T.reshape(-1, 2)
        objp = np.multiply(objp, self.square_width)
        self.object_points = objp

    def set_origin_distance(self, value):
        self.origin_distance = self.to_float(value)

    def to_int(self, value):
        try:
            value = int(value)
            if value > 0:
                return value
            else:
                return 0
        except:
            return 0

    def to_float(self, value):
        try:
            value = float(value)
            if value > 0.0:
                return value
            else:
                return 0.0
        except:
            return 0.0
