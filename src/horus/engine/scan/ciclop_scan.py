# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import time
import Queue
import numpy as np

from horus import Singleton
from horus.engine.scan.scan import Scan


class ScanError(Exception):

    def __init__(self):
        Exception.__init__(self, _("ScanError"))


@Singleton
class CiclopScan(Scan):

    """Perform Ciclop scanning algorithm:

        - Capture Thread: capture raw images and manage motor and lasers
        - Process Thread: compute 3D point cloud from raw images
    """

    def __init__(self):
        self.capture_texture = True
        self.use_left_laser = True
        self.use_right_laser = True
        self.move_motor = True
        self.motor_step = 0
        self.motor_speed = 0
        self.motor_acceleration = 0

        self._theta = 0
        self._captures_queue = Queue.Queue(100)
        self._point_cloud_queue = Queue.Queue(1000)

    def set_capture_texture(self, value):
        self.capture_texture = value

    def set_use_left_laser(self, value):
        self.use_left_laser = value

    def set_use_right_laser(self, value):
        self.use_right_laser = value

    def set_move_motor(self, value):
        self.move_motor = value

    def set_motor_step(self, value):
        self.motor_step = value

    def set_motor_speed(self, value):
        self.motor_speed = value

    def set_motor_acceleration(self, value):
        self.motor_acceleration = value

    def _initialize(self):
        self._theta = 0
        self._captures_queue.queue.clear()
        self._point_cloud_queue.queue.clear()

        #-- Setup scanner
        self.driver.board.lasers_off()
        if self.move_motor:
            self.driver.board.motor_enable()
            self.driver.board.motor_relative(self.motor_step)
            self.driver.board.motor_speed(self.motor_speed)
            self.driver.board.motor_acceleration(self.motor_acceleration)
            time.sleep(0.1)
        else:
            self.driver.board.motor_disable()

    def _capture(self):
        while self.is_scanning:
            if self._inactive:
                time.sleep(0.1)
            else:
                if abs(self._theta) > 2 * np.pi:
                    break
                else:
                    begin = time.time()
                    # Capture images
                    capture = self._capture_images()
                    # Move motor
                    if self.move_motor:
                        self.driver.board.motor_relative(self.motor_step)
                        self.driver.board.motor_move()
                    else:
                        time.sleep(0.05)
                    # Update theta
                    self._theta += np.deg2rad(self.motor_step)
                    # Refresh progress
                    if abs(self.motor_step) > 0:
                        self._progress = abs(np.rad2deg(self._theta) / self.motor_step)
                        self._range = abs(360.0 / self.motor_step)
                    # Put images into queue
                    self._captures_queue.put(capture)
                    print "Capture: {0} ms".format(int((time.time() - begin) * 1000))

        self.driver.board.lasers_off()
        self.driver.board.motor_dissable()

    def _capture_images(self):
        capture = ScanCapture()
        capture.theta = self_theta

        if self.capture_texture:
            capture.img_texture = self.image_capture.capture_texture()

        for i in xrange(2):
            # TODO: check lasers
            capture.img_laser[i] = self.image_capture.capture_laser(i)

        return capture

    def _process(self):
        ret = False
        while self.is_scanning:
            if self._inactive:
                time.sleep(0.1)
            else:
                if abs(self._theta) > 2 * np.pi:
                    self.is_scanning = False
                    break
                else:
                    begin = time.time()
                    # Get capture from queue
                    capture = self._captures_queue.get(timeout=0.1)
                    self._captures_queue.task_done()

                    for i in xrange(2):
                        if capture.img_laser[i] is not None:
                            image = capture.img_laser[i]
                            # Compute 2D points from images
                            points_2d = self.laser_segmentation.compute_2d_points(image)
                            # Compute point cloud from 2D points
                            point_cloud = self.point_cloud_generation.compute_point_cloud(
                                capture.theta, points_2d, i)
                            # Compute point cloud texture
                            if capture.img_texture is not None:
                                u, v = point_2d
                                texture = capture.img_texture[v, u.astype(int)].T
                            else:
                                img = np.zeros_like(self.laser[index])
                                img[v, u.astype(int)] = self._color
                            # Filter point cloud
                            point_cloud, texture = self.point_cloud_roi.mask_point_cloud(
                                point_cloud_roi, texture)
                            # Put point cloud into queue
                            self._point_cloud_queue.put((point_cloud, texture))
                    print "Process: {0} ms".format(int((time.time() - begin) * 1000))
        if ret:
            response = (True, None)
        else:
            response = (False, ScanError)

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
