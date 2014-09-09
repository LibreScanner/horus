#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: August 2014                                                     #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>   	                #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
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
__license__ = "GNU General Public License v3 http://www.gnu.org/licenses/gpl.html"

from horus.util.resources import *

from horus.gui.util.page import *
from horus.gui.util.imageView import *
from horus.gui.calibration.panels import *

from horus.engine.scanner import *
from horus.engine.calibration import *

class CameraIntrinsicsMainPage(Page):

	def __init__(self, parent, buttonCancelCallback=None, buttonPerformCallback=None):
		Page.__init__(self, parent,
							title=_("Camera Intrinsics"),
							left=_("Cancel"),
							right=_("Perform"),
							buttonLeftCallback=buttonCancelCallback,
							buttonRightCallback=buttonPerformCallback,
							panelOrientation=wx.HORIZONTAL)

		self.scanner = Scanner.Instance()
		self.calibration = Calibration.Instance()

		#-- Video View
		self.videoView = ImageView(self._panel)
		self.videoView.SetBackgroundColour(wx.BLACK)
		self.videoView.setImage(wx.Image(getPathForImage("bq.png")))
		
		#--Guide Panel
		self.guidePanel = wx.Panel(self._panel)
		guideBox = wx.BoxSizer(wx.VERTICAL)

		self.guideTitleText = wx.StaticText(self.guidePanel)
		self.guideTitleText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
		self.guideTitleText.SetFont( wx.Font(pointSize=16,family=wx.FONTFAMILY_DECORATIVE,style=wx.FONTSTYLE_ITALIC,weight=wx.FONTWEIGHT_NORMAL))
		self.guideTitleText.SetForegroundColour((100,100,100))

		self.guideImage = ImageView(self.guidePanel)

		self.guideProgress = ImageView(self.guidePanel)
		self.guideProgress.size = (100,100)

		guideSpacebarText = wx.StaticText(self.guidePanel, label=_("Press spacebar to continue"))

		guideBox.Add(self.guideTitleText, 0, wx.CENTER, 3)
		guideBox.Add((0, 0), 1, wx.EXPAND)
		guideBox.Add(self.guideImage, 10, wx.ALL|wx.EXPAND, 3)
		guideBox.Add((0, 0), 2, wx.EXPAND)
		guideBox.Add(self.guideProgress, 0, wx.ALL|wx.EXPAND|wx.CENTER, 3)
		guideBox.Add((0, 0), 1, wx.EXPAND)
		guideBox.Add(guideSpacebarText, 0, wx.CENTER, 3)

		self.guidePanel.SetSizer(guideBox)

		#-- Image Grid Panel
		self.imageGridPanel = wx.Panel(self._panel)
		self.rows, self.columns = 2, 6
		self.panelGrid = []
		self.gridSizer = wx.GridSizer(self.rows, self.columns, 3, 3)
		for panel in range(self.rows*self.columns):
			self.panelGrid.append(ImageView(self.imageGridPanel))
			self.panelGrid[panel].SetBackgroundColour((221, 221, 221))
			self.panelGrid[panel].setImage(wx.Image(getPathForImage("void.png")))
			self.gridSizer.Add(self.panelGrid[panel], 0, wx.ALL|wx.EXPAND)
		self.imageGridPanel.SetSizer(self.gridSizer)

		self.addToPanel(self.videoView, 2)
		self.addToPanel(self.guidePanel, 3)
		self.addToPanel(self.imageGridPanel, 3)

		self.initialize()

		self.timer = wx.Timer(self)

		#-- Events
		self.Bind(wx.EVT_SHOW, self.onShow)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
		self.videoView.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
		
		self.videoView.SetFocus()

		self.Layout()

	def initialize(self):
		self.guidePage = 0
		self.guidePanel.Show()
		self.imageGridPanel.Hide()
		self.guideTitleText.SetLabel("1. Place the pattern in the plate")
		self.guideImage.setImage(wx.Image(getPathForImage("instructions-1.png")))
		self.guideProgress.setImage(wx.Image(getPathForImage("progress-1.png")))
		self._rightButton.Disable()
		self.currentGrid = 0
		for panel in range(self.rows*self.columns):
			self.panelGrid[panel].SetBackgroundColour((221, 221, 221))
			self.panelGrid[panel].setImage(wx.Image(getPathForImage("void.png")))

	def onShow(self, event):
		self.videoManagement(event.GetShow())

	def videoManagement(self, status):
		if status:
			if not self.timer.IsRunning():
				if self.scanner.camera.fps > 0:
					mseconds = 1000/(self.scanner.camera.fps)
					self.timer.Start(milliseconds=mseconds)
					self.calibration.clearImageStack()
		else:
			self.timer.Stop()
			self.initialize()

	def onTimer(self, event):
		if self.scanner.isConnected:
			frame = self.scanner.camera.captureImage(mirror=True)
			if frame is not None:
				if self.guidePage == 3:
					self.calibration.setGuides(frame, self.currentGrid)
				self.videoView.setFrame(frame)

	def onKeyPress(self, event):
		if event.GetKeyCode() == 32: #-- spacebar
			if self.guidePage == 0:
				self.guideTitleText.SetLabel("2. Move it using the yellow lines as reference")
				self.guideImage.setImage(wx.Image(getPathForImage("instructions-2.png")))
				self.guideProgress.setImage(wx.Image(getPathForImage("progress-2.png")))
				self.guidePage = 1
			elif self.guidePage == 1:
				self.guideTitleText.SetLabel("3. Press spacebar to perform captures")
				self.guideImage.setImage(wx.Image(getPathForImage("instructions-3.png")))
				self.guideProgress.setImage(wx.Image(getPathForImage("progress-3.png")))
				self.guidePage = 2
			elif self.guidePage == 2:
				self.guidePanel.Hide()
				self.imageGridPanel.Show()
				self.Layout()
				width, height = self.scanner.camera.getResolution()
				self.calibration.generateGuides(width, height)
				self.guidePage = 3
			elif self.guidePage == 3:
				if self.scanner.isConnected:
					frame = self.scanner.camera.captureImage(mirror=False, flush=True)
					retval, frame = self.calibration.detectChessboard(frame)
					frame = cv2.flip(frame, 1) #-- Mirror
					self.addFrameToGrid(retval, frame)

	def addFrameToGrid(self, retval, image):
		if self.currentGrid < (self.columns*self.rows):
			if retval:
				self.panelGrid[self.currentGrid].setFrame(image)
				self.panelGrid[self.currentGrid].SetBackgroundColour((45,178,0))
				self.currentGrid += 1
			else:
				self.panelGrid[self.currentGrid].setFrame(image)
				self.panelGrid[self.currentGrid].SetBackgroundColour((217,0,0))

		if self.currentGrid is (self.columns*self.rows):
			self._rightButton.Enable()


class CameraIntrinsicsResultPage(Page):

	def __init__(self, parent, buttonRejectCallback=None, buttonAcceptCallback=None):
		Page.__init__(self, parent,
							title=_("Camera Intrinsics"),
							left=_("Reject"),
							right=_("Accept"),
							buttonLeftCallback=buttonRejectCallback,
							buttonRightCallback=buttonAcceptCallback,
							panelOrientation=wx.HORIZONTAL)

		self.calibration = Calibration.Instance()

		self.cameraIntrinsicsParameters = CameraIntrinsicsParameters(self._panel)

		#-- 3D Plot Panel
		self.plotPanel = Plot3DPanel(self._panel)

		self.addToPanel(self.cameraIntrinsicsParameters, 1)
		self.addToPanel(self.plotPanel, 2)

		#-- Events
		self.Bind(wx.EVT_SHOW, self.onShow)

	def onShow(self, event):
		if event.GetShow():
			self.performCalibration()

	def performCalibration(self):
		self.plotPanel.Hide()
		self.plotPanel.clear()
		ret = self.calibration.performCameraIntrinsicsCalibration()
		self.plotPanel.add(ret[2], ret[3])
		self.cameraIntrinsicsParameters.updateAllControlsToProfile(ret[0], ret[1])
		self.plotPanel.Show()


import random
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

class Plot3DPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.calibration = Calibration.Instance()

		self.initialize()

	def initialize(self):
		self.fig = Figure(tight_layout=False)
		self.canvas = FigureCanvasWxAgg(self, 1, self.fig)
		self.canvas.SetExtraStyle(wx.EXPAND)

		#self.ax = Axes3D(self.fig)
		self.ax = self.fig.gca(projection='3d', axisbg=(0.7490196,0.7490196,0.7490196,1))

		# Parameters of the pattern
		self.columns = 6
		self.rows = 11
		self.squareWidth = 13
		
		self.printCanvas()

		self.Bind(wx.EVT_SIZE, self.onSize)
		self.Layout()

	def onSize(self,event):
		self.canvas.SetClientSize(self.GetClientSize())
		self.Layout()
		event.Skip()

	def printCanvas(self):
		self.ax.plot([0,50], [0,0], [0,0], linewidth=3.0, color='red')
		self.ax.plot([0,0], [0,0], [0,50], linewidth=3.0, color='green')
		self.ax.plot([0,0], [0,50], [0,0], linewidth=3.0, color='blue')

		self.ax.set_xlabel('X')
		self.ax.set_ylabel('Z')
		self.ax.set_zlabel('Y')
		self.ax.set_xlim(-150, 150)
		self.ax.set_ylim(0, 500)
		self.ax.set_zlim(-150, 150)
		self.ax.invert_xaxis()
		self.ax.invert_yaxis()
		self.ax.invert_zaxis()

	def add(self, rvecs, tvecs):
		w = self.columns * self.squareWidth 
		h = self.rows * self.squareWidth

		p = np.array([[0,0,0],[w,0,0],[w,h,0],[0,h,0],[0,0,0]])
		n = np.array([[0,0,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]])

		c = np.array([[30,0,0],[0,30,0],[0,0,30]])

		for ind, transvector in enumerate(rvecs):

			R = cv2.Rodrigues(transvector)[0]
			t = tvecs[ind]

			points = (np.dot(R, p.T) + np.array([t,t,t,t,t]).T)[0]
			normals = np.dot(R, n.T)

			X = np.array([points[0], normals[0]])
			Y = np.array([points[1], normals[1]])
			Z = np.array([points[2], normals[2]])

			coords = (np.dot(R, c.T) + np.array([t,t,t]).T)[0]

			CX = coords[0]
			CY = coords[1]
			CZ = coords[2]

			color = (random.random(),random.random(),random.random(), 0.8)

			self.ax.plot_surface(X, Z, Y, linewidth=0, color=color)

			self.ax.plot([t[0][0],CX[0]], [t[2][0],CZ[0]], [t[1][0],CY[0]], linewidth=2.0, color='red')
			self.ax.plot([t[0][0],CX[1]], [t[2][0],CZ[1]], [t[1][0],CY[1]], linewidth=2.0, color='green')
			self.ax.plot([t[0][0],CX[2]], [t[2][0],CZ[2]], [t[1][0],CY[2]], linewidth=2.0, color='blue')
			self.canvas.draw()
		
		self.Layout()

	def clear(self):
		self.ax.cla()
		self.printCanvas()


class LaserTriangulationMainPage(Page):

	def __init__(self, parent, buttonCancelCallback=None, buttonPerformCallback=None):
		Page.__init__(self, parent,
							title=_("Laser Triangulation"),
							left=_("Cancel"),
							right=_("Perform"),
							buttonLeftCallback=buttonCancelCallback,
							buttonRightCallback=buttonPerformCallback,
							panelOrientation=wx.VERTICAL)

		detailsBox = wx.BoxSizer(wx.HORIZONTAL)

		imageView = ImageView(self._panel)
		imageView.setImage(wx.Image(getPathForImage("pattern-position.jpg")))
		detailsText = wx.StaticText(self._panel, label=_("Put the pattern on the platform"))
		detailsText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

		detailsBox.Add((0, 0), 1, wx.EXPAND)
		detailsBox.Add(detailsText, 0, wx.ALL|wx.EXPAND, 3)
		detailsBox.Add((0, 0), 1, wx.EXPAND)

		self.addToPanel(imageView, 1)
		self.addToPanel(detailsBox, 0)


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

		self.laserTriangulationParameters = LaserTriangulationParameters(self._panel)

		self.leftLaserImageSequence = LaserTriangulationImageSequence(self._panel, "Left Laser Image Sequence")
		self.rightLaserImageSequence = LaserTriangulationImageSequence(self._panel, "Right Laser Image Sequence")

		#-- Layout
		vbox.Add(self.leftLaserImageSequence, 1, wx.ALL|wx.EXPAND, 3)
		vbox.Add(self.rightLaserImageSequence, 1, wx.ALL|wx.EXPAND, 3)

		self.addToPanel(self.laserTriangulationParameters, 1)
		self.addToPanel(vbox, 3)

		#-- Events
		self.Bind(wx.EVT_SHOW, self.onShow)

	def onShow(self, event):
		if event.GetShow():
			self.performCalibration()

	def performCalibration(self):
		ret = Calibration.Instance().performLaserTriangulationCalibration()

		if ret is not None:
			self.laserTriangulationParameters.updateAllControlsToProfile(ret[1], ret[0])

			self.leftLaserImageSequence.imageLas.setFrame(ret[2][0][0])
			self.leftLaserImageSequence.imageGray.setFrame(ret[2][0][1])
			self.leftLaserImageSequence.imageBin.setFrame(ret[2][0][2])
			self.leftLaserImageSequence.imageLine.setFrame(ret[2][0][3])
			self.rightLaserImageSequence.imageLas.setFrame(ret[2][1][0])
			self.rightLaserImageSequence.imageGray.setFrame(ret[2][1][1])
			self.rightLaserImageSequence.imageBin.setFrame(ret[2][1][2])
			self.rightLaserImageSequence.imageLine.setFrame(ret[2][1][3])

class LaserTriangulationImageSequence(wx.Panel):

	def __init__(self, parent, title="Title"):
		wx.Panel.__init__(self, parent)

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)

		titleText = wx.StaticText(self, label=title)
		titleText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

		panel = wx.Panel(self)
		self.imageLas = ImageView(panel)
		self.imageGray = ImageView(panel)
		self.imageBin = ImageView(panel)
		self.imageLine = ImageView(panel)

		self.imageLas.SetBackgroundColour('#AAAAAA')
		self.imageGray.SetBackgroundColour('#AAAAAA')
		self.imageBin.SetBackgroundColour('#AAAAAA')
		self.imageLine.SetBackgroundColour('#AAAAAA')

		#-- Layout
		vbox.Add(titleText, 0, wx.ALL|wx.EXPAND, 5)
		hbox.Add(self.imageLas, 1, wx.ALL|wx.EXPAND, 3)
		hbox.Add(self.imageGray, 1, wx.ALL|wx.EXPAND, 3)
		hbox.Add(self.imageBin, 1, wx.ALL|wx.EXPAND, 3)
		hbox.Add(self.imageLine, 1, wx.ALL|wx.EXPAND, 3)
		panel.SetSizer(hbox)
		vbox.Add(panel, 1, wx.ALL|wx.EXPAND, 3)

		self.SetSizer(vbox)
		self.Layout()


class PlatformExtrinsicsMainPage(Page):

	def __init__(self, parent, buttonCancelCallback=None, buttonPerformCallback=None):
		Page.__init__(self, parent,
							title=_("Platform Extrinsics"),
							left=_("Cancel"),
							right=_("Perform"),
							buttonLeftCallback=buttonCancelCallback,
							buttonRightCallback=buttonPerformCallback,
							panelOrientation=wx.VERTICAL)

		detailsBox = wx.BoxSizer(wx.HORIZONTAL)

		imageView = ImageView(self._panel)
		imageView.setImage(wx.Image(getPathForImage("pattern-position.jpg")))
		detailsText = wx.StaticText(self._panel, label=_("Put the pattern on the platform"))
		detailsText.SetFont((wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

		detailsBox.Add((0, 0), 1, wx.EXPAND)
		detailsBox.Add(detailsText, 0, wx.ALL|wx.EXPAND, 3)
		detailsBox.Add((0, 0), 1, wx.EXPAND)

		self.addToPanel(imageView, 1)
		self.addToPanel(detailsBox, 0)


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

		self.platformExtrinsicsParameters = PlatformExtrinsicsParameters(self._panel)
		self.plotPanel = Plot2DPanel(self._panel)

		#-- Layout

		self.addToPanel(self.platformExtrinsicsParameters, 1)
		self.addToPanel(self.plotPanel, 3)

		#-- Events
		self.Bind(wx.EVT_SHOW, self.onShow)

	def onShow(self, event):
		if event.GetShow():
			self.performCalibration()

	def performCalibration(self):
		self.plotPanel.Hide()
		self.plotPanel.clear()
		ret = Calibration.Instance().performPlatformExtrinsicsCalibration()
		if ret is not None:
			xc, zc = ret[2]
			yc = np.mean(ret[0][1]) + 145 #offset
			self.plotPanel.add(ret)
			self.platformExtrinsicsParameters.updateAllControlsToProfile(np.array([[0,-1,0],[0,0,-1],[-1,0,0]]), np.array([xc, yc, zc]))
		self.plotPanel.Show()


import matplotlib.cm as cm  
import matplotlib.colors as colors

class Plot2DPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.calibration = Calibration.Instance()

		self.initialize()

	def initialize(self):
		self.fig = Figure()
		self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
		self.canvas.SetExtraStyle(wx.EXPAND)

		self.ax = self.fig.gca()
		self.ax.axis('equal')

		self.x2D = np.array([])
		self.z2D = np.array([])
		
		self.ax.set_xlabel('x')
		self.ax.set_ylabel('z')

		self.xmin = 0
		self.xmax = 1
		self.ymin = 0
		self.ymax = 1

		self.Bind(wx.EVT_SIZE, self.onSize)
		self.Layout()

	def onSize(self,event):
		self.canvas.SetClientSize(self.GetClientSize())
		self.ax.set_xlim(xmin=self.xmin, xmax=self.xmax)
		self.ax.set_ylim(ymin=self.ymin, ymax=self.ymax)
		self.canvas.draw()
		self.Layout()

	def add(self, args):
		tvecs = args[0]
		Ri = args[1]
		xc, zc = center = args[2]

		R = Ri.mean()

		x2D = tvecs[0]
		y2D = tvecs[1]
		z2D = tvecs[2]

		theta_fit = np.linspace(-np.pi, np.pi, 180)

		x_fit2 = xc + R*np.cos(theta_fit)
		z_fit2 = zc + R*np.sin(theta_fit)

		self.ax.plot(x_fit2, z_fit2, 'k--', lw=2)
		self.ax.plot([xc], [zc], 'gD', mec='r', mew=1)
		self.ax.plot(x2D, z2D, 'ro', label='Pattern corner', ms=8, mec='b', mew=1)

		self.xmin = (xc-R)/1.05
		self.xmax = (xc+R)*1.05
		self.ymin = (zc-R)/1.05
		self.ymax = (zc+R)*1.05

		vmin = min(self.xmin, self.ymin)
		vmax = max(self.xmax, self.ymax)

		nb_pts = 100

		xg, zg = np.ogrid[vmin-4*R:(vmin+4*R):nb_pts*1j, vmax-4*R:vmax+R:nb_pts*1j]
		xg = xg[..., np.newaxis]
		zg = zg[..., np.newaxis]

		Rig    = np.sqrt( (xg - x2D)**2 + (zg - z2D)**2 )
		Rig_m  = Rig.mean(axis=2)[..., np.newaxis]  
		residu = np.sum( (Rig-Rig_m)**2 ,axis=2)
		lvl = np.exp(np.linspace(np.log(residu.min()), np.log(residu.max()), 15))

		self.ax.contourf(xg.flat, zg.flat, residu.T, lvl, alpha=0.4, cmap=cm.Purples_r) # , norm=colors.LogNorm())
		self.ax.contour (xg.flat, zg.flat, residu.T, lvl, alpha=0.8, colors="lightblue")

		self.ax.grid()
		self.ax.set_title("Center: xc = "+str(xc)+"  zc = "+str(zc))

		self.canvas.draw()

		self.onSize(None)
		
		self.Layout()

	def clear(self):
		self.ax.cla()