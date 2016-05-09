# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import threading

from horus.engine.driver.driver import Driver
from horus.engine.algorithms.image_capture import ImageCapture
from horus.engine.algorithms.image_detection import ImageDetection
from horus.engine.algorithms.laser_segmentation import LaserSegmentation
from horus.engine.algorithms.point_cloud_generation import PointCloudGeneration
from horus.engine.algorithms.point_cloud_roi import PointCloudROI


class Scan(object):

    """Generic class for threading scanning"""

    def __init__(self):
        self.driver = Driver()
        self.image_capture = ImageCapture()
        self.image_detection = ImageDetection()
        self.laser_segmentation = LaserSegmentation()
        self.point_cloud_generation = PointCloudGeneration()
        self.point_cloud_roi = PointCloudROI()
        self.is_scanning = False

        # TODO: Callbacks to Observer pattern
        self._before_callback = None
        self._progress_callback = None
        self._after_callback = None
        self._progress = 0
        self._range = 0
        self._inactive = False

    def set_callbacks(self, before, progress, after):
        self._before_callback = before
        self._progress_callback = progress
        self._after_callback = after

    def start(self):
        if not self.is_scanning:
            if self._before_callback is not None:
                self._before_callback()

            if self._progress_callback is not None:
                self._progress_callback(0)

            self._initialize()

            self.is_scanning = True
            self._inactive = False

            threading.Thread(target=self._capture).start()
            threading.Thread(target=self._process).start()

    def stop(self):
        self._inactive = False
        self.is_scanning = False

    def pause(self):
        self._inactive = True

    def resume(self):
        self._inactive = False

    def _initialize(self):
        pass

    def _capture(self):
        pass

    def _process(self):
        pass
