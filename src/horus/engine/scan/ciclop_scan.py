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


@Singleton
class CiclopScan(Scan):

    """Perform Ciclop scanning algorithm:

        - Capture Thread: capture raw images and manage motor and lasers
        - Process Thread: compute 3D point cloud from raw images
    """

    def __init__(self):
        self.capture_texture = True
        self.remove_background = True
        self.use_left_laser = True
        self.use_right_laser = True
        self.move_motor = True
        self.motor_step = 0
        self.motor_speed = 0
        self.motor_acceleration = 0
        self.exposure_texture = 0
        self.exposure_laser = 0

        self._theta = 0
        self._images_queue = Queue.Queue(100)
        self._point_cloud_queue = Queue.Queue(1000)

    def set_capture_texture(self, value):
        self.capture_texture = value

    def set_remove_background(self, value):
        self.remove_background = value

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

    def set_exposure_texture(self, value):
        self.exposure_texture = value

    def set_exposure_laser(self, value):
        self.exposure_laser = value

    def getImage(self, value):
        pass

    def _initialize(self):
        self._theta = 0
        self._images_queue.queue.clear()
        self._point_cloud_queue.queue.clear()

        #-- Setup scanner
        self.driver.camera.capture_image()
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
                    images = self._capture_images()

                    # Move motor
                    if self.move_motor:
                        #self.driver.board.motor_relative(self.motor_step)
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
                    self._images_queue.put(images)

                    print "Capture: {0} ms".format(int((time.time() - begin) * 1000))

        board.lasers_off()
        board.motor_dissable()

    def _capture_images(self):
        captures = segmentation.Captures()
        captures.theta = self_theta

        # TODO: custom flush for each OS

        if self.capture_texture:
            self.driver.board.lasers_off()
            self.driver.camera.set_exposure(self.exposure_texture)
            captures.img_texture = self.driver.camera.capture_image(flush=1)

        if self.remove_background:
            self.driver.board.lasers_off()
            self.driver.camera.set_exposure(self.exposure_laser)
            captures.img_no_laser = self.driver.camera.capture_image(flush=1)

        if self.use_left_laser:
            self.driver.board.laser_left_on()
            self.driver.board.laser_right_off()
            self.driver.camera.set_exposure(self.exposure_laser)
            captures.img_laser[0] = self.driver.camera.capture_image(flush=1)

        if self.use_right_laser:
            self.driver.board.laser_left_off()
            self.driver.board.laser_right_on()
            self.driver.camera.set_exposure(self.exposure_laser)
            captures.img_laser[1] = self.driver.camera.capture_image(flush=1)

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
