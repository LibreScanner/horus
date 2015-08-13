# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import cv2
import wx._core
import numpy as np

import random
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

import horus.util.error as Error
from horus.util import profile, resources

from horus.gui.util.imageView import ImageView, VideoView

from horus.gui.workbench.calibration.page import Page

from horus.engine.driver.driver import Driver
from horus.engine.calibration.pattern import Pattern
from horus.engine.calibration.camera_intrinsics import CameraIntrinsics, CameraIntrinsicsError
from horus.engine.calibration.laser_triangulation import LaserTriangulation
from horus.engine.calibration.platform_extrinsics import PlatformExtrinsics

driver = Driver()
pattern = Pattern()
camera_intrinsics = CameraIntrinsics()
laser_triangulation = LaserTriangulation()
platform_extrinsics = PlatformExtrinsics()


class CameraIntrinsicsMainPage(Page):

    def __init__(self, parent, afterCancelCallback=None, afterCalibrationCallback=None):
        Page.__init__(self, parent,
                      title=_("Camera Intrinsics"),
                      subTitle=_("Press space bar to perform captures"),
                      left=_("Cancel"),
                      right=_("Calibrate"),
                      buttonLeftCallback=self.onCancel,
                      buttonRightCallback=self.onCalibrate,
                      panelOrientation=wx.HORIZONTAL,
                      viewProgress=True)

        self.afterCancelCallback = afterCancelCallback
        self.afterCalibrationCallback = afterCalibrationCallback

        # Video View
        self.videoView = VideoView(self._panel, self.getFrame, 50)
        self.videoView.SetBackgroundColour(wx.BLACK)

        # Image Grid Panel
        self.imageGridPanel = wx.Panel(self._panel)
        self.rows, self.columns = 3, 5
        self.panelGrid = []
        self.gridSizer = wx.GridSizer(self.rows, self.columns, 3, 3)
        for panel in xrange(self.rows * self.columns):
            self.panelGrid.append(ImageView(self.imageGridPanel))
            self.panelGrid[panel].Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
            self.panelGrid[panel].SetBackgroundColour((221, 221, 221))
            self.panelGrid[panel].setImage(wx.Image(resources.getPathForImage("void.png")))
            self.gridSizer.Add(self.panelGrid[panel], 0, wx.ALL | wx.EXPAND)
        self.imageGridPanel.SetSizer(self.gridSizer)

        # Layout
        self.addToPanel(self.videoView, 1)
        self.addToPanel(self.imageGridPanel, 3)

        # Events
        self.Bind(wx.EVT_SHOW, self.onShow)
        self.videoView.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.imageGridPanel.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)

        self.videoView.SetFocus()
        self.Layout()

    def initialize(self):
        self._rightButton.Hide()
        self.subTitleText.SetLabel(_("Press space bar to perform captures"))
        self.currentGrid = 0
        self.gauge.SetValue(0)
        for panel in xrange(self.rows * self.columns):
            self.panelGrid[panel].SetBackgroundColour((221, 221, 221))
            self.panelGrid[panel].setImage(wx.Image(resources.getPathForImage("void.png")))

    def onShow(self, event):
        if event.GetShow():
            self.gauge.SetValue(0)
            self.videoView.play()
            camera_intrinsics.reset()
            self.GetParent().Layout()
            self.Layout()
        else:
            try:
                self.initialize()
                self.videoView.stop()
            except:
                pass

    def getFrame(self):
        frame = driver.camera.capture_image()
        retval, frame, _ = camera_intrinsics.draw_chessboard(frame)
        if retval:
            self.videoView.SetBackgroundColour((45, 178, 0))
        else:
            self.videoView.SetBackgroundColour((217, 0, 0))
        return frame

    def onKeyPress(self, event):
        if event.GetKeyCode() == 32:  # spacebar
            self.videoView.pause()
            ret, frame = camera_intrinsics.capture()
            if ret:
                self.addFrameToGrid(frame)
                if self.currentGrid <= self.rows * self.columns:
                    self.gauge.SetValue(self.currentGrid * 100.0 / self.rows / self.columns)
            self.videoView.play()

    def addFrameToGrid(self, image):
        if self.currentGrid < (self.columns * self.rows):
            self.panelGrid[self.currentGrid].setFrame(image)
            self.currentGrid += 1
        if self.currentGrid is (self.columns * self.rows):
            self.subTitleText.SetLabel(_("Press Calibrate to continue"))
            self.buttonRightCallback()
            # self._rightButton.Enable()

    def onCalibrate(self):
        camera_intrinsics.set_callbacks(lambda: wx.CallAfter(self.beforeCalibration),
                                        None,
                                        lambda r: wx.CallAfter(self.afterCalibration, r))
        camera_intrinsics.start()

    def beforeCalibration(self):
        self.videoView.pause()
        self._rightButton.Disable()
        if not hasattr(self, 'waitCursor'):
            self.waitCursor = wx.BusyCursor()

    def afterCalibration(self, result):
        self._rightButton.Enable()
        if self.afterCalibrationCallback is not None:
            self.afterCalibrationCallback(result)
        if hasattr(self, 'waitCursor'):
            del self.waitCursor

    def onCancel(self):
        boardUnplugCallback = driver.board.unplug_callback
        cameraUnplugCallback = driver.camera.unplug_callback
        driver.board.set_unplug_callback(None)
        driver.camera.set_unplug_callback(None)
        if not hasattr(self, 'waitCursor'):
            self.waitCursor = wx.BusyCursor()
        self.onCalibration = False
        camera_intrinsics.cancel()
        if self.afterCancelCallback is not None:
            self.afterCancelCallback()
        del self.waitCursor
        driver.board.set_unplug_callback(boardUnplugCallback)
        driver.camera.set_unplug_callback(cameraUnplugCallback)


class CameraIntrinsicsResultPage(Page):

    def __init__(self, parent, buttonRejectCallback=None, buttonAcceptCallback=None):
        Page.__init__(self, parent,
                      title=_("Camera Intrinsics"),
                      left=_("Reject"),
                      right=_("Accept"),
                      buttonLeftCallback=buttonRejectCallback,
                      buttonRightCallback=buttonAcceptCallback,
                      panelOrientation=wx.HORIZONTAL)

        #-- 3D Plot Panel
        self.plotPanel = CameraIntrinsics3DPlot(self._panel)

        #-- Layout
        self.addToPanel(self.plotPanel, 2)

        #-- Events
        self.Bind(wx.EVT_SHOW, self.onShow)

    def onShow(self, event):
        if event.GetShow():
            self.GetParent().Layout()
            self.Layout()

    def processCalibration(self, response):
        self.plotPanel.Hide()
        self.plotPanel.clear()
        ret, result = response

        if ret:
            error, mtx, dist, rvecs, tvecs = result
            self.GetParent().GetParent().controls.panels[
                'camera_intrinsics_panel'].setParameters((mtx, dist))
            self.plotPanel.add(error, rvecs, tvecs)
            self.plotPanel.Show()
            self.Layout()
        else:
            if isinstance(result, CameraIntrinsicsError):
                dlg = wx.MessageDialog(self, _("Camera Intrinsics Calibration has failed. Please try again."), _(
                    result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()


class CameraIntrinsics3DPlot(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.initialize()

    def initialize(self):
        self.fig = Figure(facecolor=(0.7490196, 0.7490196, 0.7490196, 1), tight_layout=True)
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        self.canvas.SetExtraStyle(wx.EXPAND)

        self.ax = self.fig.gca(projection='3d', axisbg=(0.7490196, 0.7490196, 0.7490196, 1))

        self.printCanvas()

        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Layout()

    def onSize(self, event):
        self.canvas.SetClientSize(self.GetClientSize())
        self.Layout()
        event.Skip()

    def printCanvas(self):
        self.ax.plot([0, 50], [0, 0], [0, 0], linewidth=2.0, color='red')
        self.ax.plot([0, 0], [0, 0], [0, 50], linewidth=2.0, color='green')
        self.ax.plot([0, 0], [0, 50], [0, 0], linewidth=2.0, color='blue')

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Z')
        self.ax.set_zlabel('Y')
        self.ax.set_xlim(-150, 150)
        self.ax.set_ylim(0, 500)
        self.ax.set_zlim(-150, 150)
        self.ax.invert_xaxis()
        self.ax.invert_yaxis()
        self.ax.invert_zaxis()

    def add(self, error, rvecs, tvecs):
        w = pattern.columns * pattern.square_width
        h = pattern.rows * pattern.square_width

        p = np.array([[0, 0, 0], [w, 0, 0], [w, h, 0], [0, h, 0], [0, 0, 0]])
        n = np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]])

        c = np.array([[30, 0, 0], [0, 30, 0], [0, 0, -30]])

        self.ax.text(-100, 200, 0, str(round(error, 5)), fontsize=15)

        for ind, transvector in enumerate(rvecs):

            R = cv2.Rodrigues(transvector)[0]
            t = tvecs[ind]

            points = (np.dot(R, p.T) + np.array([t, t, t, t, t]).T)[0]
            normals = np.dot(R, n.T)

            X = np.array([points[0], normals[0]])
            Y = np.array([points[1], normals[1]])
            Z = np.array([points[2], normals[2]])

            coords = (np.dot(R, c.T) + np.array([t, t, t]).T)[0]

            CX = coords[0]
            CY = coords[1]
            CZ = coords[2]

            color = (random.random(), random.random(), random.random(), 0.8)

            self.ax.plot_surface(X, Z, Y, linewidth=0, color=color)

            self.ax.plot([t[0][0], CX[0]], [t[2][0], CZ[0]],
                         [t[1][0], CY[0]], linewidth=1.0, color='green')
            self.ax.plot([t[0][0], CX[1]], [t[2][0], CZ[1]],
                         [t[1][0], CY[1]], linewidth=1.0, color='red')
            self.ax.plot([t[0][0], CX[2]], [t[2][0], CZ[2]],
                         [t[1][0], CY[2]], linewidth=1.0, color='blue')
            self.canvas.draw()

        self.Layout()

    def clear(self):
        self.ax.cla()
        self.printCanvas()


class LaserTriangulationMainPage(Page):

    def __init__(self, parent, afterCancelCallback=None, afterCalibrationCallback=None):
        Page.__init__(self, parent,
                      title=_("Laser Triangulation"),
                      subTitle=_(
                          "Put the pattern on the platform as shown in the picture and press Calibrate to continue"),
                      left=_("Cancel"),
                      right=_("Calibrate"),
                      buttonLeftCallback=self.onCancel,
                      buttonRightCallback=self.onCalibrate,
                      panelOrientation=wx.HORIZONTAL,
                      viewProgress=True)

        self.onCalibration = False

        self.afterCancelCallback = afterCancelCallback
        self.afterCalibrationCallback = afterCalibrationCallback

        #-- Image View
        imageView = ImageView(self._panel)
        imageView.setImage(wx.Image(resources.getPathForImage("pattern-position-right.jpg")))

        #-- Video View
        self.videoView = VideoView(self._panel, self.getFrame, 50)
        self.videoView.SetBackgroundColour(wx.BLACK)

        #-- Layout
        self.addToPanel(imageView, 3)
        self.addToPanel(self.videoView, 2)

        #-- Events
        self.Bind(wx.EVT_SHOW, self.onShow)

        self.Layout()

    def initialize(self):
        self.gauge.SetValue(0)
        self._rightButton.Enable()

    def onShow(self, event):
        if event.GetShow():
            self.videoView.play()
            self.GetParent().Layout()
            self.Layout()
        else:
            try:
                self.initialize()
                self.videoView.stop()
            except:
                pass

    def getFrame(self):
        if self.onCalibration:
            frame = laser_triangulation.image
        else:
            frame = driver.camera.capture_image()

        # if frame is not None:
        #	retval, frame = calibration.detect_chessboard(frame)
        return frame

    def onCalibrate(self):
        self.onCalibration = True
        laser_triangulation.image = driver.camera.capture_image()
        laser_triangulation.threshold = profile.getProfileSettingFloat('laser_threshold_value')
        laser_triangulation.exposure_normal = profile.getProfileSettingNumpy(
            'exposure_calibration')
        laser_triangulation.exposure_laser = profile.getProfileSettingNumpy(
            'exposure_calibration') / 2.

        laser_triangulation.set_callbacks(lambda: wx.CallAfter(self.beforeCalibration),
                                          None,
                                          lambda r: wx.CallAfter(self.afterCalibration, r))
        laser_triangulation.start()

    def beforeCalibration(self):
        self._rightButton.Disable()
        self.waitCursor = wx.BusyCursor()

    def afterCalibration(self, result):
        self.onCalibrationFinished(result)
        self.onCalibration = False

    def onCalibrationFinished(self, result):
        self._rightButton.Enable()
        if self.afterCalibrationCallback is not None:
            self.afterCalibrationCallback(result)
        if hasattr(self, 'waitCursor'):
            del self.waitCursor

    def onCancel(self):
        boardUnplugCallback = driver.board.unplug_callback
        cameraUnplugCallback = driver.camera.unplug_callback
        driver.board.set_unplug_callback(None)
        driver.camera.set_unplug_callback(None)
        if not hasattr(self, 'waitCursor'):
            self.waitCursor = wx.BusyCursor()
        self.onCalibration = False
        laser_triangulation.cancel()
        if self.afterCancelCallback is not None:
            self.afterCancelCallback()
        del self.waitCursor
        driver.board.set_unplug_callback(boardUnplugCallback)
        driver.camera.set_unplug_callback(cameraUnplugCallback)


class LaserTriangulationResultPage(Page):

    def __init__(self, parent, buttonRejectCallback=None, buttonAcceptCallback=None):
        Page.__init__(self, parent,
                      title=_("Laser Triangulation"),
                      left=_("Reject"),
                      right=_("Accept"),
                      buttonLeftCallback=buttonRejectCallback,
                      buttonRightCallback=buttonAcceptCallback,
                      panelOrientation=wx.HORIZONTAL)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.plotPanel = LaserTriangulation3DPlot(self._panel)

        #-- Layout
        self.addToPanel(self.plotPanel, 3)

        #-- Events
        self.Bind(wx.EVT_SHOW, self.onShow)

    def onShow(self, event):
        if event.GetShow():
            self.GetParent().Layout()
            self.Layout()

    def processCalibration(self, response):
        ret, result = response

        if ret:
            dL = result[0][0]
            nL = result[0][1]
            stdL = result[0][2]
            dR = result[1][0]
            nR = result[1][1]
            stdR = result[1][2]

            self.GetParent().GetParent().controls.panels[
                'laser_triangulation_panel'].setParameters((dL, nL, dR, nR))
            self.plotPanel.clear()
            self.plotPanel.add((dL, nL, stdL, dR, nR, stdR))
            self.plotPanel.Show()
            self.Layout()
        else:
            if result == Error.CalibrationError:
                dlg = wx.MessageDialog(self, _("Laser Triangulation Calibration has failed. Please try again."), _(
                    result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()


class LaserTriangulation3DPlot(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.initialize()

    def initialize(self):
        fig = Figure(facecolor=(0.7490196, 0.7490196, 0.7490196, 1), tight_layout=True)
        self.canvas = FigureCanvasWxAgg(self, -1, fig)
        self.canvas.SetExtraStyle(wx.EXPAND)
        self.ax = fig.gca(projection='3d', axisbg=(0.7490196, 0.7490196, 0.7490196, 1))

        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Layout()

    def onSize(self, event):
        self.canvas.SetClientSize(self.GetClientSize())
        self.canvas.draw()
        self.Layout()

    def add(self, args):
        dL, nL, stdL, dR, nR, stdR = args

        rL = np.cross(np.array([0, 0, 1]), nL)
        sL = np.cross(rL, nL)
        RL = np.array([rL, sL, nL])

        rR = np.cross(np.array([0, 0, 1]), nR)
        sR = np.cross(rR, nR)
        RR = np.array([rR, sR, nR])

        self.addPlane(RL, dL * nL)
        self.addPlane(RR, dR * nR)

        self.ax.plot([0, 50], [0, 0], [0, 0], linewidth=2.0, color='red')
        self.ax.plot([0, 0], [0, 0], [0, 50], linewidth=2.0, color='green')
        self.ax.plot([0, 0], [0, 50], [0, 0], linewidth=2.0, color='blue')

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Z')
        self.ax.set_zlabel('Y')

        self.ax.text(-100, 0, 0, str(round(stdL, 5)), fontsize=15)
        self.ax.text(100, 0, 0, str(round(stdR, 5)), fontsize=15)

        self.ax.set_xlim(-150, 150)
        self.ax.set_ylim(0, 400)
        self.ax.set_zlim(-150, 150)

        self.ax.invert_xaxis()
        self.ax.invert_yaxis()
        self.ax.invert_zaxis()

        self.canvas.draw()
        self.Layout()

    def addPlane(self, R, t):
        w = 200
        h = 300

        p = np.array([[-w / 2, -h / 2, 0], [-w / 2, h / 2, 0],
                      [w / 2, h / 2, 0], [w / 2, -h / 2, 0], [-w / 2, -h / 2, 0]])
        n = np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]])

        self.ax.plot([0, t[0]], [0, t[2]], [0, t[1]], linewidth=2.0, color='yellow')

        points = np.dot(R.T, p.T) + np.array([t, t, t, t, t]).T
        normals = np.dot(R.T, n.T)

        X = np.array([points[0], normals[0]])
        Y = np.array([points[1], normals[1]])
        Z = np.array([points[2], normals[2]])

        self.ax.plot_surface(X, Z, Y, linewidth=0, color=(1, 0, 0, 0.8))

        self.canvas.draw()

    def clear(self):
        self.ax.cla()


class PlatformExtrinsicsMainPage(Page):

    def __init__(self, parent, afterCancelCallback=None, afterCalibrationCallback=None):
        Page.__init__(self, parent,
                      title=_("Platform Extrinsics"),
                      subTitle=_(
                          "Put the pattern on the platform as shown in the picture and press Calibrate to continue"),
                      left=_("Cancel"),
                      right=_("Calibrate"),
                      buttonLeftCallback=self.onCancel,
                      buttonRightCallback=self.onCalibrate,
                      panelOrientation=wx.HORIZONTAL,
                      viewProgress=True)

        self.onCalibration = False

        self.afterCancelCallback = afterCancelCallback
        self.afterCalibrationCallback = afterCalibrationCallback

        #-- Image View
        imageView = ImageView(self._panel)
        imageView.setImage(wx.Image(resources.getPathForImage("pattern-position-left.jpg")))

        #-- Video View
        self.videoView = VideoView(self._panel, self.getFrame, 50)
        self.videoView.SetBackgroundColour(wx.BLACK)

        #-- Layout
        self.addToPanel(imageView, 3)
        self.addToPanel(self.videoView, 2)

        #-- Events
        self.Bind(wx.EVT_SHOW, self.onShow)

        self.Layout()

    def initialize(self):
        self.gauge.SetValue(0)
        self._rightButton.Enable()

    def onShow(self, event):
        if event.GetShow():
            self.videoView.play()
            self.GetParent().Layout()
            self.Layout()
        else:
            try:
                self.initialize()
                self.videoView.stop()
            except:
                pass

    def getFrame(self):
        if self.onCalibration:
            frame = platform_extrinsics.image
        else:
            frame = driver.camera.capture_image()
        _,frame,_ = calibration.draw_chessboard(frame)

        return frame

    def onCalibrate(self):
        self.onCalibration = True
        platform_extrinsics.image = driver.camera.capture_image()

        platform_extrinsics.set_callbacks(lambda: wx.CallAfter(self.beforeCalibration),
                                          lambda p: wx.CallAfter(self.progressCalibration, p),
                                          lambda r: wx.CallAfter(self.afterCalibration, r))
        platform_extrinsics.start()

    def beforeCalibration(self):
        self._rightButton.Disable()
        self.gauge.SetValue(0)
        self.waitCursor = wx.BusyCursor()

    def progressCalibration(self, progress):
        self.gauge.SetValue(progress)

    def afterCalibration(self, result):
        self.onCalibrationFinished(result)
        self.onCalibration = False

    def onCalibrationFinished(self, result):
        self._rightButton.Enable()
        if self.afterCalibrationCallback is not None:
            self.afterCalibrationCallback(result)
        if hasattr(self, 'waitCursor'):
            del self.waitCursor

    def onCancel(self):
        boardUnplugCallback = driver.board.unplug_callback
        cameraUnplugCallback = driver.camera.unplug_callback
        driver.board.set_unplug_callback(None)
        driver.camera.set_unplug_callback(None)
        if not hasattr(self, 'waitCursor'):
            self.waitCursor = wx.BusyCursor()
        self.onCalibration = False
        platform_extrinsics.cancel()
        if self.afterCancelCallback is not None:
            self.afterCancelCallback()
        del self.waitCursor
        driver.board.set_unplug_callback(boardUnplugCallback)
        driver.camera.set_unplug_callback(cameraUnplugCallback)


class PlatformExtrinsicsResultPage(Page):

    def __init__(self, parent, buttonRejectCallback=None, buttonAcceptCallback=None):
        Page.__init__(self, parent,
                      title=_("Platform Extrinsics"),
                      left=_("Reject"),
                      right=_("Accept"),
                      buttonLeftCallback=buttonRejectCallback,
                      buttonRightCallback=buttonAcceptCallback,
                      panelOrientation=wx.HORIZONTAL)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.plotPanel = PlatformExtrinsics3DPlot(self._panel)

        #-- Layout
        self.addToPanel(self.plotPanel, 3)

        #-- Events
        self.Bind(wx.EVT_SHOW, self.onShow)

    def onShow(self, event):
        if event.GetShow():
            self.GetParent().Layout()
            self.Layout()

    def processCalibration(self, response):
        ret, result = response

        if ret:
            R = result[0]
            t = result[1]
            self.GetParent().GetParent().controls.panels[
                'platform_extrinsics_panel'].setParameters((R, t))
            self.plotPanel.clear()
            self.plotPanel.add(result)
            self.plotPanel.Show()
            self.Layout()
        else:
            if result == Error.CalibrationError:
                dlg = wx.MessageDialog(self, _("Platform Extrinsics Calibration has failed. Please try again."), _(
                    result), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()


class PlatformExtrinsics3DPlot(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.initialize()

    def initialize(self):
        fig = Figure(facecolor=(0.7490196, 0.7490196, 0.7490196, 1), tight_layout=True)
        self.canvas = FigureCanvasWxAgg(self, -1, fig)
        self.canvas.SetExtraStyle(wx.EXPAND)
        self.ax = fig.gca(projection='3d', axisbg=(0.7490196, 0.7490196, 0.7490196, 1))

        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Layout()

    def onSize(self, event):
        self.canvas.SetClientSize(self.GetClientSize())
        self.canvas.draw()
        self.Layout()

    def add(self, args):
        R, t, center, point, normal, [x, y, z], circle = args

        # plot the surface, data, and synthetic circle
        self.ax.scatter(x, z, y, c='b', marker='o')
        #self.ax.scatter(center[0], center[2], center[1], c='b', marker='o')
        self.ax.plot(circle[0], circle[2], circle[1], c='r')

        d = pattern.distance

        self.ax.plot([t[0], t[0] + 50 * R[0][0]], [t[2], t[2] + 50 * R[2][0]],
                     [t[1], t[1] + 50 * R[1][0]], linewidth=2.0, color='red')
        self.ax.plot([t[0], t[0] + 50 * R[0][1]], [t[2], t[2] + 50 * R[2][1]],
                     [t[1], t[1] + 50 * R[1][1]], linewidth=2.0, color='green')
        self.ax.plot([t[0], t[0] + d * R[0][2]], [t[2], t[2] + d * R[2][2]],
                     [t[1], t[1] + d * R[1][2]], linewidth=2.0, color='blue')

        self.ax.plot([0, 50], [0, 0], [0, 0], linewidth=2.0, color='red')
        self.ax.plot([0, 0], [0, 0], [0, 50], linewidth=2.0, color='green')
        self.ax.plot([0, 0], [0, 50], [0, 0], linewidth=2.0, color='blue')

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Z')
        self.ax.set_zlabel('Y')

        self.ax.set_xlim(-150, 150)
        self.ax.set_ylim(0, 400)
        self.ax.set_zlim(-150, 150)

        self.ax.invert_xaxis()
        self.ax.invert_yaxis()
        self.ax.invert_zaxis()

        self.canvas.draw()
        self.Layout()

    def clear(self):
        self.ax.cla()
