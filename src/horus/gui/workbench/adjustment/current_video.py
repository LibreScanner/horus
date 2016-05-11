# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import time

from horus import Singleton
from horus.gui.engine import image_capture, image_detection, laser_segmentation


@Singleton
class CurrentVideo(object):

    def __init__(self):
        self.mode = 'Texture'
        self.updating = False
        self.latest_image = None
        self.capturing = False

    def get_frame(self):
        if not self.updating:
            self.latest_image = self.capture()
        return self.latest_image

    def capture(self):
        self.capturing = True
        image = None

        if self.mode == 'Texture':
            image = image_capture.capture_texture()

        if self.mode == 'Pattern':
            image = image_capture.capture_pattern()
            image = image_detection.detect_pattern(image)

        if self.mode == 'Laser':
            image = image_capture.capture_all_lasers()

        if self.mode == 'Gray':
            images = image_capture.capture_lasers()
            for i in xrange(2):
                images[i] = laser_segmentation.compute_line_segmentation(images[i])
            if images[0] is not None and images[1] is not None:
                image = images[0] + images[1]
                image = cv2.merge((image, image, image))
            else:
                image = None

        self.capturing = False
        return image

    def sync(self):
        # Wait until latest capture is completed
        while self.capturing:
            time.sleep(0.05)

    def flush(self):
        if self.mode == 'Texture':
            for i in range(2):
                image_capture.flush_texture()
        elif self.mode == 'Pattern':
            for i in range(2):
                image_capture.flush_pattern()
        else:
            for i in range(1):
                image_capture.flush_laser()
