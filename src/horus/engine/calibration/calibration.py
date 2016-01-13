# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import platform
import threading

from horus.engine.driver.driver import Driver

from horus.engine.calibration.pattern import Pattern
from horus.engine.calibration.calibration_data import CalibrationData

from horus.engine.algorithms.image_capture import ImageCapture
from horus.engine.algorithms.image_detection import ImageDetection
from horus.engine.algorithms.laser_segmentation import LaserSegmentation
from horus.engine.algorithms.point_cloud_generation import PointCloudGeneration

system = platform.system()

"""
    Calibrations:

        - Autocheck Algorithm
        - Camera Intrinsics Calibration
        - Laser Triangulation Calibration
        - Platform Extrinsics Calibration
"""


class CalibrationCancel(Exception):

    def __init__(self):
        Exception.__init__(self, "CalibrationCancel")


class Calibration(object):

    """Generic class for threading calibration"""

    def __init__(self):
        self.driver = Driver()
        self.pattern = Pattern()
        self.calibration_data = CalibrationData()
        self.image_capture = ImageCapture()
        self.image_detection = ImageDetection()
        self.laser_segmentation = LaserSegmentation()
        self.point_cloud_generation = PointCloudGeneration()

        # TODO: Callbacks to Observer pattern
        self._before_callback = None
        self._progress_callback = None
        self._after_callback = None
        self._is_calibrating = False

    def set_callbacks(self, before, progress, after):
        self._before_callback = before
        self._progress_callback = progress
        self._after_callback = after

    def start(self):
        if not self._is_calibrating:
            if self._before_callback is not None:
                self._before_callback()

            if self._progress_callback is not None:
                self._progress_callback(0)

            self._is_calibrating = True
            threading.Thread(target=self._start).start()

    def _start(self):
        pass

    def cancel(self):
        self._is_calibrating = False
