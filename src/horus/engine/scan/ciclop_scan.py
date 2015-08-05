# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import time
import Queue
import numpy as np

from horus.engine.scan.scan import Scan
from horus.engine.driver.driver import Driver
from horus.engine.algorithms.laser_segmentation import LaserSegmentation
from horus.engine.algorithms.point_cloud_generation import PointCloudGeneration

driver = Driver()
board = driver.board
camera = driver.camera
laser_segmentation = LaserSegmentation()
point_cloud_generation = PointCloudGeneration()


class CiclopScan(Scan):

    """Perform Ciclop scanning algorithm:

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
                    images = self._capture_images()

                    # Move motor
                    if self.move_motor:
                        board.motor_relative(self.motor_step)
                        board.motor_move()
                    else:
                        time.sleep(0.05)

                    # Update theta
                    self._theta += np.deg2rad(self.motor_step)

                    # Refresh progress
                    if abs(self.motor_step) > 0:
                        self._progress = abs(np.rad2deg(self._theta) / self.motor_step)
                        self._range = abs(360.0 / self.motor_step)

                    # Put images into queue
                    self._images_queue.put(images)

                    print "Capture: {0} ms".format(int((time.time() - begin) * 1000))

        board.lasers_off()
        board.motor_dissable()

    def _capture_images(self):
        captures = segmentation.Captures()
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
            captures.img_laser[0] = camera.capture_image(flush=1)

        if self.use_right_laser:
            board.laser_left_off()
            board.laser_right_on()
            camera.set_exposure(self.exposure_laser)
            captures.img_laser[1] = camera.capture_image(flush=1)

        return captures

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

                    # Get images from queue
                    images = self._images_queue.get(timeout=0.1)
                    self._images_queue.task_done()

                    # Compute 2D points from images
                    points2D = laser_segmentation.compute_2D_points(images)

                    # Texture
                    if images.img_texture is None:
                        temp = np.ones_like(images.img_texture)
                        temp[:, :, 0] *= images.color[0]
                        temp[:, :, 1] *= images.color[1]
                        temp[:, :, 2] *= images.color[2]
                        img_texture = temp
                    else:
                        img_texture = images.img_texture

                    #texture = img_texture[v, u.astype(int)].T

                    """
                    #-- Compute 3D points
                    points3D, colors = self.pcg.compute3DPoints(points2D, \
                        colors, laser, updateTheta)
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
