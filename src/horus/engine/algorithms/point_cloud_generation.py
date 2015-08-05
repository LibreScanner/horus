# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'


import numpy as np

from horus.util.singleton import Singleton


@Singleton
class PointCloudGenerator(object):

    """Contain point cloud generation algorithms:

            - Point cloud generation and filtering
    """

    def __init__(self):
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
