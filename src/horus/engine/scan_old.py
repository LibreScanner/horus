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



    def _processThread(self, afterCallback):
        """"""
        ret = False

        self.progress = 0

        while self.runProcess:
            if not self.inactive:
                angle = abs(self.pcg.theta * 180.0 / np.pi)
                if abs(self.pcg.degrees) > 0:
                    self.progress = abs(angle / self.pcg.degrees)
                    self.range = abs(360.0 / self.pcg.degrees)
                if angle <= 360.0:
                    if not self.imagesQueue.empty():
                        imagesQueueItem = self.imagesQueue.get(timeout=0.1)
                        self.imagesQueue.task_done()

                        begin = time.time()

                        updateTheta = True
                        #-- Compute 2D points from images
                        points2D, colors = self.compute2DPoints(imagesQueueItem)
                        #-- Put 2D points into the queue
                        if imagesQueueItem[0] == 'right':
                            laser = False
                        elif imagesQueueItem[0] == 'left':
                            laser = True
                        elif imagesQueueItem[0] == 'both_right':
                            updateTheta = False
                            laser = False
                        elif imagesQueueItem[0] == 'both_left':
                            updateTheta = True
                            laser = True

                        #-- Compute 3D points
                        points3D, colors = self.pcg.compute3DPoints(
                            points2D, colors, laser, updateTheta)

                        if points3D is not None and colors is not None:
                            if self.generatePointCloud:
                                #-- Put point cloud into the queue
                                self.points3DQueue.put((points3D, colors))

                        end = time.time()

                        print "Process: {0} ms".format(int((end - begin) * 1000))

                        #-- Free objects
                        del imagesQueueItem
                        del colors
                        del points2D
                        del points3D
                else:
                    if self.generatePointCloud:
                        ret = True
                        self._stopProcess()
            else:
                time.sleep(0.1)

        if ret:
            response = (True, None)
        else:
            response = (False, Error.ScanError)

        self.imgLaser = None
        self.imgGray = None
        self.imgLine = None
        self.imgColor = None

        self.points3DQueue.queue.clear()
        self.imagesQueue.queue.clear()

        if afterCallback is not None:
            afterCallback(response)

    def getProgress(self):
        return self.progress, self.range

    def getPointCloudIncrement(self):
        """ """
        if not self.points3DQueue.empty():
            pc = self.points3DQueue.get_nowait()
            if pc is not None:
                self.points3DQueue.task_done()
            return pc
        else:
            return None



    def compute2DPoints(self, image_info):
        image = image_info[1]
        self.imgLaser = image
        tempColor = np.ones_like(image)
        tempColor[:, :, 0] *= self.color[0]
        tempColor[:, :, 1] *= self.color[1]
        tempColor[:, :, 2] *= self.color[2]
        self.imgColor = tempColor

        #-- Convert tp Y Cr Cb format
        y, cr, cb = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YCR_CB))

        #-- Get Cr
        image = cr

        #-- Apply ROI mask
        image = self.applyROIMask(image)

        #-- Threshold image
        if self.thresholdEnable:
            image = cv2.threshold(image, self.thresholdValue, 255.0, cv2.THRESH_TOZERO)[1]

        #-- Peak detection: center of mass
        h, w = image.shape
        W = np.array((np.matrix(np.linspace(0, w - 1, w)).T * np.matrix(np.ones(h))).T)
        s = image.sum(axis=1)
        v = np.where(s > 0)[0]
        u = (W * image).sum(axis=1)[v] / s[v]

        tempLine = np.zeros_like(self.imgLaser)
        tempLine[v, u.astype(int)] = 255
        self.imgLine = tempLine
        self.imgGray = cv2.merge((image, image, image))

        colors = np.array(np.matrix(np.ones(len(u))).T * np.matrix(self.color)).T

        return (u, v), colors



    def compute2DPoints(self, images):
        imageColor = images[1]
        imageLaser = images[2]
        self.imgLaser = imageLaser
        self.imgColor = imageColor

        """#-- Use R channel
        r1,g1,b1 = cv2.split(imageColor)
        r2,g1,b2 = cv2.split(imageLaser)

        image = cv2.subtract(r2, r1)"""

        #-- Use Cr channel
        y1, cr1, cb1 = cv2.split(cv2.cvtColor(imageColor, cv2.COLOR_RGB2YCR_CB))
        y2, cr2, cb2 = cv2.split(cv2.cvtColor(imageLaser, cv2.COLOR_RGB2YCR_CB))

        image = cv2.subtract(cr2, cr1)

        #-- Apply ROI mask
        image = self.applyROIMask(image)

        #-- Open image
        if self.openEnable:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.openValue, self.openValue))
            image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

        #-- Threshold image
        if self.thresholdEnable:
            image = cv2.threshold(image, self.thresholdValue, 255.0, cv2.THRESH_TOZERO)[1]

        #-- Peak detection: center of mass
        h, w = image.shape
        W = np.array((np.matrix(np.linspace(0, w - 1, w)).T * np.matrix(np.ones(h))).T)
        s = image.sum(axis=1)
        v = np.where(s > 0)[0]
        u = (W * image).sum(axis=1)[v] / s[v]

        tempLine = np.zeros_like(imageLaser)
        tempLine[v, u.astype(int)] = 255.0
        self.imgLine = tempLine
        self.imgGray = cv2.merge((image, image, image))

        colors = imageColor[v, u.astype(int)].T

        return (u, v), colors


@Singleton
class PointCloudGenerator:

    """Contains all scanning algorithms:

                    - Point cloud generation and filtering
    """

    def __init__(self):
        self.theta = 0
        self.driver = Driver.Instance()

        self.rad = np.pi / 180.0

        self.umin = 0
        self.umax = 960
        self.vmin = 0
        self.vmax = 1280

        self.circleResolution = 30
        self.circleArray = np.array([[np.cos(i * 2 * np.pi / self.circleResolution) for i in xrange(self.circleResolution)],
                                     [np.sin(i * 2 * np.pi / self.circleResolution)
                                      for i in xrange(self.circleResolution)],
                                     np.zeros(self.circleResolution)])

    def setViewROI(self, value):
        self.viewROI = value

    def setViewCenter(self, value):
        self.viewCenter = value

    def setROIDiameter(self, value):
        self.roiRadius = value / 2.0
        self.calculateROI()

    def setROIHeight(self, value):
        self.roiHeight = value
        self.calculateROI()

    def setDegrees(self, degrees):
        self.degrees = degrees

    def setResolution(self, width, height):
        self.width = width
        self.height = height
        self.W = np.ones((height, width)) * np.linspace(0, width - 1, width)

    def setUseLaser(self, useLeft, useRight):
        self.useLeftLaser = useLeft
        self.useRightLaser = useRight

    def setLaserAngles(self, angleLeft, angleRight):
        self.alphaLeft = angleLeft * self.rad
        self.alphaRight = angleRight * self.rad

    def setCameraIntrinsics(self, cameraMatrix, distortionVector):
        self.fx = cameraMatrix[0][0]
        self.fy = cameraMatrix[1][1]
        self.cx = cameraMatrix[0][2]
        self.cy = cameraMatrix[1][2]

    def setLaserTriangulation(self, dL, nL, dR, nR):
        self.dL = dL
        self.nL = nL
        self.dR = dR
        self.nR = nR

    def setPlatformExtrinsics(self, rotationMatrix, translationVector):
        self.rotationMatrix = rotationMatrix
        self.translationVector = translationVector

    def resetTheta(self):
        self.theta = 0

    def calculateROI(self):
        if hasattr(self, 'roiRadius') and \
           hasattr(self, 'roiHeight') and \
           hasattr(self, 'rotationMatrix') and \
           hasattr(self, 'translationVector') and \
           hasattr(self, 'fx') and hasattr(self, 'fy') and \
           hasattr(self, 'cx') and hasattr(self, 'cy') and \
           hasattr(self, 'width') and hasattr(self, 'height'):

            #-- Platform system
            bottom = np.matrix(self.roiRadius * self.circleArray)
            top = bottom + np.matrix([0, 0, self.roiHeight]).T
            data = np.concatenate((bottom, top), axis=1)

            #-- Camera system
            data = self.rotationMatrix * data + np.matrix(self.translationVector).T

            #-- Video system
            u = self.fx * data[0] / data[2] + self.cx
            v = self.fy * data[1] / data[2] + self.cy

            umin = int(round(np.min(u)))
            umax = int(round(np.max(u)))
            vmin = int(round(np.min(v)))
            vmax = int(round(np.max(v)))

            # visualization :
            v_ = np.array(v.T)
            # lower cylinder base
            a = v_[:(len(v_) / 2)]
            # upper cylinder base
            b = v_[(len(v_) / 2):]
            self.lower_vmin = int(round(np.max(a)))
            self.lower_vmax = int(round(np.min(a)))
            self.upper_vmin = int(round(np.min(b)))
            self.upper_vmax = int(round(np.max(b)))

            self.no_trimmed_umin = umin
            self.no_trimmed_umax = int(round(np.max(u)))
            self.no_trimmed_vmin = int(round(np.min(v)))
            self.no_trimmed_vmax = int(round(np.max(v)))

            self.umin = max(umin, 0)
            self.umax = min(umax, self.width)
            self.vmin = max(vmin, 0)
            self.vmax = min(vmax, self.height)

    def calculateCenter(self):
        #-- Platform system
        bottom = np.matrix(0 * self.circleArray)
        top = bottom + np.matrix([0, 0, 0]).T
        data = np.concatenate((bottom, top), axis=1)

        #-- Camera system
        data = self.rotationMatrix * data + np.matrix(self.translationVector).T

        #-- Video system
        u = self.fx * data[0] / data[2] + self.cx
        v = self.fy * data[1] / data[2] + self.cy

        umin = int(round(np.min(u)))
        umax = int(round(np.max(u)))
        vmin = int(round(np.min(v)))
        vmax = int(round(np.max(v)))

        self.center_u = umin + (umax - umin) / 2
        self.center_v = vmin + (vmax - vmin) / 2

    def pointCloudGeneration(self, points2D, leftLaser=True):
        """ """
        u, v = points2D

        #-- Obtaining point cloud in camera coordinates
        if leftLaser:
            d = self.dL
            n = self.nL
        else:
            d = self.dR
            n = self.nR

        # x = np.concatenate(((u-self.cx)/self.fx, (v-self.cy)/self.fy, np.ones(len(u)))).reshape(3,len(u))

        x = np.concatenate(
            ((u - self.cx) / self.fx, (v - self.cy) / self.fy, np.ones(len(u)))).reshape(3, len(u))

        Xc = d / np.dot(n, x) * x

        #-- Move point cloud to world coordinates
        R = np.matrix(self.rotationMatrix).T
        t = np.matrix(self.translationVector).T

        Xwo = R * Xc - R * t

        #-- Rotate point cloud
        c = np.cos(self.theta)
        s = np.sin(self.theta)
        Rz = np.matrix([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        Xw = Rz * Xwo

        #-- Return result
        if Xw.size > 0:
            return np.array(Xw)
        else:
            return None

    def pointCloudFilter(self, points, colors):
        """ """
        #-- Point Cloud Filter
        rho = np.sqrt(points[0, :] ** 2 + points[1, :] ** 2)
        z = points[2, :]

        idx = np.where((z >= 0) &
                       (z <= self.roiHeight) &
                       (rho >= -self.roiRadius) &
                       (rho <= self.roiRadius))[0]

        return points[:, idx], colors[:, idx]

    def compute3DPoints(self, points2D, colors, leftLaser, updateTheta):
        """ """
        #-- Point Cloud Generation
        points3D = self.pointCloudGeneration(points2D, leftLaser)

        if points3D is not None:
            #-- Point Cloud Filter
            points3D, colors = self.pointCloudFilter(points3D, colors)

        if updateTheta:
            #-- Update Theta
            self.theta -= self.degrees * self.rad

        return points3D, colors
