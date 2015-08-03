#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014-2015 Mundo Reader S.L.                             #
#                                                                       #
# Date: March, December 2014, July 2015                                 #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 2 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.  #
#                                                                       #
#-----------------------------------------------------------------------#

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl.html"

import cv2
import time
import Queue
import threading
import numpy as np

from driver import Driver

import horus.util.error as Error
from horus.util.singleton import Singleton
from horus.util import system as sys

# Common

driver = Driver.Instance()
board = driver.board
camera = driver.camera
pcg = PointCloudGenerator.Instance()


class Scan(object):

    """Generic class for threading scanning"""

    def __init__(self):
        # TODO: Callbacks to Observer pattern
        self._before_callback = None
        self._progress_callback = None
        self._after_callback = None
        self._progress = 0
        self._range = 0
        self._is_scanning = False
        self._paused = False

    def set_callbacks(self, before, progress, after):
        self._before_callback = before
        self._progress_callback = progress
        self._after_callback = after

    def start(self):
        if not self._is_scanning:
            if self._before_callback is not None:
                self._before_callback()

            if self._progress_callback is not None:
                self._progress_callback(0)

            self._initialize()

            self._is_scanning = True
            self._paused = False

            threading.Thread(target=self._capture).start()
            threading.Thread(target=self._process).start()

    def stop(self):
        self._is_scanning = False
        self._inactive = False

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


class Captures(object):

    def __init__(self):
        self.theta = 0
        self.img_texture = None
        self.img_no_laser = None
        self.img_laser_left = None
        self.img_laser_right = None


class CiclopScan(Scan):

    """Performs Ciclop scanning algorithm:

        - Capture Thread: capture raw images and manage motor and lasers
        - Process Thread: compute 3D point cloud from raw images
    """

    def __init__(self):
        self.with_difference = True
        self.with_texture = True
        self.exposure_texture = 0
        self.exposure_laser = 0
        self.use_left_laser = True
        self.use_right_laser = True
        self.move_motor = True
        self.motor_step = 0
        self.motor_speed = 0
        self.motor_acceleration = 0
        # self.fast_scan = False

        self._theta = 0
        self._img_type = 'laser'
        self._images = {'laser': None,
                        'gray': None,
                        'line': None,
                        'color': None}
        self._images_queue = Queue.Queue(100)
        self._point_cloud_queue = Queue.Queue(1000)

    def _initialize(self):
        self._theta = 0
        self._images_queue.queue.clear()
        self._point_cloud_queue.queue.clear()

        #-- Setup scanner
        camera.capture_image()
        board.lasers_off()
        if self.move_motor:
            board.motor_enable()
            board.motor_speed(self.motor_speed)
            board.motor_acceleration(self.motor_acceleration)
            time.sleep(0.1)
        else:
            board.motor_disable()

    """def get_image(self, source=None):
        if source is None:
            img = self._images[self._img_type]
        else:
            img = source

        if img is not None:
            if self.pcg.viewROI:
                img = self.roi2DVisualization(img)
        return img

    # TODO: refactor
    def roi2DVisualization(self, img):
        self.pcg.calculateCenter()
        # params:
        thickness = 6
        thickness_hiden = 1

        center_up_u = self.pcg.no_trimmed_umin + \
            (self.pcg.no_trimmed_umax - self.pcg.no_trimmed_umin) / 2
        center_up_v = self.pcg.upper_vmin + (self.pcg.upper_vmax - self.pcg.upper_vmin) / 2
        center_down_u = self.pcg.no_trimmed_umin + \
            (self.pcg.no_trimmed_umax - self.pcg.no_trimmed_umin) / 2
        center_down_v = self.pcg.lower_vmax + (self.pcg.lower_vmin - self.pcg.lower_vmax) / 2
        axes_up = ((self.pcg.no_trimmed_umax - self.pcg.no_trimmed_umin) / 2,
                   ((self.pcg.upper_vmax - self.pcg.upper_vmin) / 2))
        axes_down = ((self.pcg.no_trimmed_umax - self.pcg.no_trimmed_umin) / 2,
                     ((self.pcg.lower_vmin - self.pcg.lower_vmax) / 2))

        img = img.copy()
        # upper ellipse
        if (center_up_v < self.pcg.cy):
            cv2.ellipse(img, (center_up_u, center_up_v), axes_up,
                        0, 180, 360, (0, 100, 200), thickness)
            cv2.ellipse(img, (center_up_u, center_up_v), axes_up,
                        0, 0, 180, (0, 100, 200), thickness_hiden)
        else:
            cv2.ellipse(img, (center_up_u, center_up_v), axes_up,
                        0, 180, 360, (0, 100, 200), thickness)
            cv2.ellipse(img, (center_up_u, center_up_v), axes_up,
                        0, 0, 180, (0, 100, 200), thickness)

        # lower ellipse
        cv2.ellipse(img, (center_down_u, center_down_v), axes_down,
                    0, 180, 360, (0, 100, 200), thickness_hiden)
        cv2.ellipse(img, (center_down_u, center_down_v),
                    axes_down, 0, 0, 180, (0, 100, 200), thickness)

        # cylinder lines

        cv2.line(img, (self.pcg.no_trimmed_umin, center_up_v),
                 (self.pcg.no_trimmed_umin, center_down_v), (0, 100, 200), thickness)
        cv2.line(img, (self.pcg.no_trimmed_umax, center_up_v),
                 (self.pcg.no_trimmed_umax, center_down_v), (0, 100, 200), thickness)

        # view center
        if axes_up[0] <= 0 or axes_up[1] <= 0:
            axes_up_center = (20, 1)
            axes_down_center = (20, 1)
        else:
            axes_up_center = (20, axes_up[1] * 20 / axes_up[0])
            axes_down_center = (20, axes_down[1] * 20 / axes_down[0])
        # upper center
        cv2.ellipse(img, (self.pcg.center_u, min(center_up_v, self.pcg.center_v)),
                    axes_up_center, 0, 0, 360, (0, 70, 120), -1)
        # lower center
        cv2.ellipse(img, (self.pcg.center_u, self.pcg.center_v),
                    axes_down_center, 0, 0, 360, (0, 70, 120), -1)

        return img

    def applyROIMask(self, image):
        mask = np.zeros(image.shape, np.uint8)
        mask[self.pcg.vmin:self.pcg.vmax,
             self.pcg.umin:self.pcg.umax] = image[self.pcg.vmin:self.pcg.vmax,
                                                  self.pcg.umin:self.pcg.umax]

        return mask"""

    def _capture(self):
        while self._is_scanning:
            if self._inactive:
                time.sleep(0.1)
            else:
                if abs(self._theta) > 2 * np.pi:
                    break
                else:
                    begin = time.time()

                    # Capture images
                    images = self._capture_images()

                    # Move motor
                    if self.move_motor:
                        board.motor_relative(self.motor_step)
                        board.motor_move()
                    else:
                        time.sleep(0.05)

                    # Update theta
                    self._theta += np.deg2rad(self.motor_step)

                    # Put images into queue
                    self._images_queue.put(images)

                    print "Capture: {0} ms".format(int((time.time() - begin) * 1000))

        board.lasers_off()
        board.motor_dissable()

    def _capture_images(self):
        captures = Captures()
        captures.theta = self_theta

        # TODO: custom flush for each OS

        if self.with_texture:
            board.lasers_off()
            camera.set_exposure(self.exposure_texture)
            captures.img_texture = camera.capture_image(flush=1)

        if self.with_difference:
            board.lasers_off()
            camera.set_exposure(self.exposure_laser)
            captures.img_no_laser = camera.capture_image(flush=1)

        if self.use_left_laser:
            board.laser_left_on()
            board.laser_right_off()
            camera.set_exposure(self.exposure_laser)
            captures.img_laser_left = camera.capture_image(flush=1)

        if self.use_right_laser:
            board.laser_left_off()
            board.laser_right_on()
            camera.set_exposure(self.exposure_laser)
            captures.img_laser_right = camera.capture_image(flush=1)

        return captures

    def _process(self):
        ret = False

        while self._is_scanning:
            if self._inactive:
                time.sleep(0.1)
            else:
                if abs(self._theta) > 2 * np.pi:
                    self._is_scanning = False
                    break
                else:
                    begin = time.time()

                    # Get images from queue
                    images = self._images_queue.get(timeout=0.1)
                    self._images_queue.task_done()

                    # Refresh progress
                    if abs(self.motor_step) > 0:
                        self._progress = abs(np.rad2deg(self._theta) / self.motor_step)
                        self._range = abs(360.0 / self.motor_step)

                    """
                    # Compute 2D points from images
                    points2D, colors = self.compute2DPoints(images)

                    #-- Compute 3D points
                    points3D, colors = self.pcg.compute3DPoints(points2D, colors, laser, updateTheta)
                    """

                    # Put point cloud into queue
                    self.pointsQueue.put((points3D, colors))


                    print "Process: {0} ms".format(int((time.time() - begin) * 1000))
        if ret:
            response = (True, None)
        else:
            response = (False, _("Scan Error"))

        if self._after_callback is not None:
            self._after_callback(response)

    def get_progress(self):
        return self._progress, self._range

    def get_point_cloud_increment(self):
        if not self._point_cloud_queue.empty():
            pc = self._point_cloud_queue.get_nowait()
            if pc is not None:
                self._point_cloud_queue.task_done()
            return pc
        else:
            return None
