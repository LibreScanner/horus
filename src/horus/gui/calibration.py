#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: June 2014                                                       #
# Author: Jesús Arroyo Torrens <jesus.arroyo@bq.com>                    #
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

__author__ = u"Carlos Crespo <carlos.crespo@bq.com>"
__license__ = u"GNU General Public License v3 http://www.gnu.org/licenses/gpl.html"

from horus.gui.util.workbench import *
from horus.gui.util.page import *
from horus.gui.util.videoView import *
from horus.util import resources



import random
import numpy as np

import matplotlib
matplotlib.interactive( True )
matplotlib.use( 'WXAgg' )
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure
import cv2

from scipy import optimize   
import matplotlib.cm as cm  
import matplotlib.colors as colors

class CalibrationWorkbench(Workbench):

	def __init__(self, parent):
		Workbench.__init__(self, parent, 1, 1)
		self.scanner = self.GetParent().scanner
		self.calibration = self.GetParent().calibration
		self.load()

	def load(self):

		# self.toolbar.AddLabelTool(wx.ID_EXIT, '', wx.Bitmap(resources.getPathForImage("connect.png")))
		# self.toolbar.Realize()

		self._panel.parent=self
		self._intrinsicsPanel=IntrinsicsPanel(self._panel,self.calibration)
		self._extrinsicsPanel=ExtrinsicsPanel(self._panel,self.calibration)

		hbox = wx.BoxSizer(wx.HORIZONTAL)

		hbox.Add(self._intrinsicsPanel,1,wx.EXPAND|wx.ALL,40)
		hbox.Add(self._extrinsicsPanel,1,wx.EXPAND|wx.ALL,40)
		self._panel.SetSizer(hbox)

		# self.loadExtrinsicCalibrationPanel(0)

	def loadInit(self,event):
		
		if hasattr(self,'_extrinsicCalibrationPanel'):
			self._extrinsicCalibrationPanel.hide()
		if hasattr(self,'_patternPanel'):
			self._patternPanel.Show(False)
		if hasattr(self,'_plotPanel'):
			self._plotPanel.hide()
		self._intrinsicsPanel.Show(True)
		self._intrinsicsPanel.reload()
		self._extrinsicsPanel.Show(True)

	def loadPagePattern(self,event):
		self._intrinsicsPanel.Show(False)
		self._extrinsicsPanel.Show(False)
		if not hasattr(self,'_patternPanel'):
			self._patternPanel=PatternPanel(self._panel,self.scanner,self.calibration)			
		else:
			self._patternPanel.Show(True)
			if hasattr(self,'_plotPanel'):
				self._plotPanel.hide()

			self._patternPanel.clear()
			self._patternPanel.videoView.SetFocus()
	def loadPagePlot(self,event):
		self._patternPanel.Show(False)
		if not hasattr(self,'_plotPanel'):
			self._plotPanel=PlotPanel(self._panel,self.calibration)
		else:
			self._plotPanel.reload()
			self._plotPanel.show()
	def loadExtrinsicCalibrationPanel(self,event):
		self._intrinsicsPanel.Show(False)
		self._extrinsicsPanel.Show(False)
		if not hasattr(self,'_extrinsicCalibrationPanel'):
			self._extrinsicCalibrationPanel=ExtrinsicCalibrationPanel(self._panel,self.scanner)
		else:
			self._extrinsicCalibrationPanel.Show(True)
			self._extrinsicCalibrationPanel.guideView.Show(True)
			self._extrinsicCalibrationPanel.videoView.SetFocus()
			self._extrinsicCalibrationPanel.getRightButton().Bind(wx.EVT_BUTTON,self._extrinsicCalibrationPanel.start)

class PatternPanel(Page):
	def __init__(self,parent,scanner,calibration):
		Page.__init__(self,parent)
		self.parent=parent;
		

		self.load() 
		self.scanner=scanner
		self.calibration=calibration
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
		self.getLeftButton().Bind(wx.EVT_BUTTON,self.parent.parent.loadInit)

		# self.getRightButton().Bind(wx.EVT_BUTTON,self.parent.parent.loadPagePlot)
		self.getRightButton().Bind(wx.EVT_BUTTON,self.calibrateCamera)
		self.getRightButton().SetLabel("Calibrate!")
		self.loaded=False
		self.currentGrid=0
		# set quantity of photos to take
		self.rows=2
		self.columns=6
	def load(self):

		self.videoView = VideoView(self._upPanel)
		self.guideView = VideoView(self._upPanel)
		hbox= wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.videoView,2,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.guideView,5,wx.EXPAND|wx.ALL,1)
		self.guideView.setImage(wx.Image(getPathForImage("keyboard.png")))
		self.text=wx.StaticText(self.guideView,label=_("Press the space bar to perform captures moninas"))		
		self._upPanel.SetSizer(hbox)

		self.playTool= self.parent.parent.toolbar.AddLabelTool(wx.NewId(), _("Initialize camera"), wx.Bitmap(getPathForImage("play.png")), shortHelp=_("Play"))
				
		self.snapshotTool= self.parent.parent.toolbar.AddLabelTool(wx.NewId(), _("Snapshot"), wx.Bitmap(getPathForImage("snapshot.png")), shortHelp=_("Snapshot"))
				
		self.parent.parent.toolbar.Realize()

		self.parent.parent.Bind(wx.EVT_TOOL, self.onPlayToolClicked, self.playTool)
				
		self.parent.parent.Bind(wx.EVT_TOOL, self.onSnapshotToolClicked, self.snapshotTool)

		self.videoView.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)
		# cool hack: key event listener only works if the focus is in some elements like our videoview
		self.videoView.SetFocus()

		self._title=wx.StaticText(self.getTitlePanel(),label=_("Intrinsic calibration (Step 1): camera calibration"))
		font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.FONTWEIGHT_BOLD,True)
		self._title.SetFont(font)
		self._subTitle=wx.StaticText(self.getTitlePanel(),label=_("Place the pattern adjusting it to the grid"))
		
		vbox=wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self._title,0,wx.LEFT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 10)	
		vbox.Add(self._subTitle,0,wx.LEFT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 10)	
		
		self.getTitlePanel().SetSizer(vbox)
		self.Layout()
		self.ghbox = wx.BoxSizer(wx.HORIZONTAL)
		self.ghbox.Add(self,1,wx.EXPAND,0)
		self.parent.SetSizer(self.ghbox)
  		self.parent.parent.Layout()
		
	def onPlayToolClicked(self, event):
		
		self.OnKeyPress(0)

	def onSnapshotToolClicked(self, event):
		
		frame = self.scanner.camera.captureImage(False)
		self.addToGrid(frame)

	def onTimer(self, event):
		frame = self.scanner.camera.captureImage(True)
		self.videoView.setFrame(frame)

	def OnKeyPress(self,event):
		if not self.loaded:
			self.scanner.connect()
			self.timer.Start(milliseconds=150)
			self.loaded=True
			self.loadGrid()
			print event.GetKeyCode()
		elif event.GetKeyCode()==32:
			frame = self.scanner.camera.captureImage(True)
			frame,retval= self.calibration.detectPrintChessboard(frame)
			self.addToGrid(frame,retval)
		
	def loadGrid(self):
		self.guideView.Show(False)
		self.gridPanel=wx.Panel(self._upPanel, id=wx.ID_ANY,style=wx.SUNKEN_BORDER)
		hbox= wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.videoView,2,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.gridPanel,5,wx.EXPAND|wx.ALL,1)
		self._upPanel.SetSizer(hbox)
		
		gs=wx.GridSizer(self.rows,self.columns,3,3)
		self.panelGrid=[]
		for panel in range(self.rows*self.columns):

			self.panelGrid.append(VideoView(self.gridPanel))
			self.panelGrid[panel].SetBackgroundColour((random.randrange(255),random.randrange(255),random.randrange(255)))	
			self.panelGrid[panel].index=panel
			gs.Add(self.panelGrid[panel],0,wx.EXPAND)
			self.panelGrid[panel].Bind(wx.EVT_LEFT_DOWN,self.onClick)
		self.gridPanel.SetSizer(gs)
		self.Layout()

	def addToGrid(self,image,retval):
		if self.currentGrid<(self.columns*self.rows):
			if retval:
				self.panelGrid[self.currentGrid].setFrame(image)
				self.panelGrid[self.currentGrid].SetBackgroundColour((0,255,0))
				self.currentGrid+=1

			else:
				self.panelGrid[self.currentGrid].setFrame(image)
				self.panelGrid[self.currentGrid].SetBackgroundColour((255,0,0))
		else:
			self.currentGrid=0
			self.panelGrid[self.currentGrid].setFrame(image)
			self.currentGrid+=1

	def clear(self):
		if hasattr(self,'panelGrid'):
			for panel in self.panelGrid:
				panel.Destroy()
				print "Destroy the panel"
			self.loadGrid()
		self.currentGrid=0
		self.calibration.clearData()
	def onClick(self,event):
		# TODO removable on click
		print event.GetEventObject()
		obj=event.GetEventObject()
		obj.SetBackgroundColour((random.randrange(255),random.randrange(255),random.randrange(255)))	
		print obj.index

	def calibrateCamera(self,event):
		self.calibration.calibrationFromImages()
		self.parent.parent.loadPagePlot(0)


class PlotPanel(Page):
	def __init__(self,parent,calibration):
		Page.__init__(self,parent)
		self.calibration=calibration
		self.parent=parent;
		self.getLeftButton().Bind(wx.EVT_BUTTON,self.parent.parent.loadPagePattern)
		self.getRightButton().Bind(wx.EVT_BUTTON,self.parent.parent.loadInit)
		

		
		self.load()
	def load(self):
		self.rvecsTrain= self.calibration.rvecs
		self.tvecsTrain= self.calibration.tvecs

		self.fig = Figure(tight_layout=True)
		self.canvas = FigureCanvasWxAgg( self.getPanel(), -1, self.fig)
		self.canvas.SetExtraStyle(wx.EXPAND)

		self.ax = self.fig.gca(projection='3d',axisbg=(0.1843, 0.3098, 0.3098))
		self.getPanel().Bind(wx.EVT_SIZE, self.on_size)
		# Parameters of the pattern
		self.columns=5
		self.rows=8
		self.squareWidth=12
		self.nPoints=100
		# Basis for the pattern
		self.x = np.linspace(0, self.squareWidth*self.columns, self.nPoints)
		self.y = np.linspace(0, self.squareWidth*self.rows, self.nPoints)
		self.x=self.x[np.newaxis]
		self.y=self.y[np.newaxis]
		self.x=self.x.T
		self.y=self.y.T
		self.z=np.zeros(np.shape(self.x))
		# do the grid horizontal
		self.testMatrix = [0,0,0]
		for xColumns in range(self.columns+1):
			x=np.empty(np.shape(self.x))
			x.fill(xColumns*self.squareWidth)
			y=self.y
			z=self.z
			auxTestMatrix=np.hstack((x,y,z))
			self.testMatrix=np.vstack((self.testMatrix,auxTestMatrix))
		# do the grid vertical
		for yRows in range(self.rows+1):
			x=self.x
			y=np.empty(np.shape(self.y))
			y.fill(yRows*self.squareWidth)
			z=self.z
			auxTestMatrix=np.hstack((x,y,z))
			self.testMatrix=np.vstack((self.testMatrix,auxTestMatrix))
		# plot the pattern
		# for i in range(self.columns+self.rows+2):
		# 	plotable=self.testMatrix[i*self.nPoints+1:i*self.nPoints+self.nPoints,:]
		# 	self.ax.plot(plotable[:,0],plotable[:,2],plotable[:,1])
		self.printCanvas()
		print "loading plot"
		self._title=wx.StaticText(self.getTitlePanel(),label=_("Intrinsic calibration (Step 2): plot monin"))
		font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.FONTWEIGHT_BOLD,True)
		self._title.SetFont(font)
		self._subTitle=wx.StaticText(self.getTitlePanel(),label=_("Here you can see the seUXy plot"))
		
		vbox=wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self._title,0,wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 1)	
		vbox.Add(self._subTitle,0,wx.TOP|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 10)	
		
		self.getTitlePanel().SetSizer(vbox)
		self.Layout()
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self,1,wx.EXPAND,0)
		self.parent.SetSizer(hbox)
		self.parent.parent.Layout()

	def on_size(self,event):
		pix = self.getPanel().GetClientSize()
		self.fig.set_size_inches(pix[0]/self.fig.get_dpi(),pix[1]/self.fig.get_dpi())
		x,y = self.getPanel().GetSize()  
		self.canvas.SetClientSize((x, y))
		self.canvas.draw()
		event.Skip()
		

	def printCanvas(self):
		axisXx,axisXy,axisXz=[0,50],[0,0],[0,0]
		axisYx,axisYy,axisYz=[0,0],[0,50],[0,0]
		axisZx,axisZy,axisZz=[0,0],[0,0],[0,50]
		self.ax.plot(axisXx,axisXy,axisXz,linewidth=3.0,color='red')
		self.ax.plot(axisYx,axisYy,axisYz,linewidth=3.0,color='blue')
		self.ax.plot(axisZx,axisZy,axisZz,linewidth=3.0,color='green')

		self.ax.set_xlabel('X')
		self.ax.set_ylabel('Z')
		self.ax.set_zlabel('Y')
		self.ax.set_xlim(-150, 150)
		self.ax.set_ylim(0, 300)
		self.ax.set_zlim(-150, 150)
		self.ax.invert_xaxis()
		self.ax.invert_yaxis()
		self.ax.invert_zaxis()
		#remove next line, add to button
		self.addToCanvas()
	def addToCanvas(self):
		self.rotation=self.rvecsTrain
		self.translation=self.tvecsTrain
		axisXx,axisXy,axisXz=[0,30],[0,0],[0,0]
		axisYx,axisYy,axisYz=[0,0],[0,30],[0,0]
		axisZx,axisZy,axisZz=[0,0],[0,0],[0,30]
		for ind,transvector in enumerate(self.rotation): 
			rtAxisXx,rtAxisXy,rtAxisXz=np.zeros(len(axisXx)),np.zeros(len(axisXy)),np.zeros(len(axisXz))
			rtAxisYx,rtAxisYy,rtAxisYz=np.zeros(len(axisYx)),np.zeros(len(axisYy)),np.zeros(len(axisYz))
			rtAxisZx,rtAxisZy,rtAxisZz=np.zeros(len(axisZx)),np.zeros(len(axisZy)),np.zeros(len(axisZz))
			rotTemp,jacob=cv2.Rodrigues(transvector)
			transTemp=self.translation[ind]
			for indAxis,pointAxis in enumerate( axisXx):
				bx= np.asarray([[axisXx[indAxis]],[axisXy[indAxis]],[axisXz[indAxis]]])
				rtAxisX=(np.dot(rotTemp,bx)+transTemp)
				rtAxisXx.itemset(indAxis,rtAxisX.item(0))
				rtAxisXy.itemset(indAxis,rtAxisX.item(1))
				rtAxisXz.itemset(indAxis,rtAxisX.item(2))
				by= np.asarray([[axisYx[indAxis]],[axisYy[indAxis]],[axisYz[indAxis]]])
				rtAxisY=(np.dot(rotTemp,by)+transTemp)
				rtAxisYx.itemset(indAxis,rtAxisY.item(0))
				rtAxisYy.itemset(indAxis,rtAxisY.item(1))
				rtAxisYz.itemset(indAxis,rtAxisY.item(2))
				bz= np.asarray([[axisZx[indAxis]],[axisZy[indAxis]],[axisZz[indAxis]]])
				rtAxisZ=(np.dot(rotTemp,bz)+transTemp)
				rtAxisZx.itemset(indAxis,rtAxisZ.item(0))
				rtAxisZy.itemset(indAxis,rtAxisZ.item(1))
				rtAxisZz.itemset(indAxis,rtAxisZ.item(2))
			for index,vector in enumerate(self.testMatrix):
					vector=vector[np.newaxis]
					vector=vector.T
					rtvector= (np.dot(rotTemp,vector)+ transTemp)
					rtvector=rtvector.T
					if (index==0):
						self.rtTestMatrix=rtvector
					else:
						self.rtTestMatrix=np.vstack((self.rtTestMatrix,rtvector))
			color=(random.random(),random.random(),random.random(),0.5)
			for i in range(self.columns+self.rows+2):
				
				plotable=self.rtTestMatrix[i*self.nPoints+1:i*self.nPoints+self.nPoints,:]
				self.ax.plot(plotable[:,0],plotable[:,2],plotable[:,1],linewidth=4,color=color)
			self.ax.plot(rtAxisXx,rtAxisXz,rtAxisXy,linewidth=2.0,color='red')
			self.ax.plot(rtAxisYx,rtAxisYz,rtAxisYy,linewidth=2.0,color='green')
			self.ax.plot(rtAxisZx,rtAxisZz,rtAxisZy,linewidth=2.0,color='blue')
			
			self.canvas.draw()

	def clearPlot(self):
		self.ax.cla()
		self.printCanvas()
		self.canvas.draw()
	def hide(self):
		self.canvas.Show(False)
		self.Show(False)
		self.getPanel().Unbind(wx.EVT_SIZE)
	def show(self):
		self.canvas.Show(True)
		self.Show(True)
		self.getPanel().Bind(wx.EVT_SIZE,self.on_size)
	def reload(self):
		self.clearPlot()
		self.load()

class ExtrinsicCalibrationPanel(Page):
	def __init__(self,parent,scanner):
		Page.__init__(self,parent)
		self.scanner=scanner
		self.parent=parent;
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
		self.getLeftButton().Bind(wx.EVT_BUTTON,self.parent.parent.loadInit)
		self.getRightButton().Bind(wx.EVT_BUTTON,self.start)
		self.loaded=False
		self.load()

		self.workingOnExtrinsic=True


	def load(self):
		self.videoView = VideoView(self._upPanel)
		self.guideView = VideoView(self._upPanel)
		hbox= wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.videoView,2,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.guideView,5,wx.EXPAND|wx.ALL,1)
		self.guideView.setImage(wx.Image(getPathForImage("keyboard.png")))
		self.text=wx.StaticText(self.guideView,label=_("Place the pattern in the indicated position and press the space bar to perform captures moninas"))		
		self._upPanel.SetSizer(hbox)

		self.playTool= self.parent.parent.toolbar.AddLabelTool(wx.NewId(), _("Initialize camera"), wx.Bitmap(getPathForImage("play.png")), shortHelp=_("Play"))
				
		self.snapshotTool= self.parent.parent.toolbar.AddLabelTool(wx.NewId(), _("Snapshot"), wx.Bitmap(getPathForImage("snapshot.png")), shortHelp=_("Snapshot"))
				
		self.parent.parent.toolbar.Realize()

		self.parent.parent.Bind(wx.EVT_TOOL, self.onPlayToolClicked, self.playTool)
				
		self.parent.parent.Bind(wx.EVT_TOOL, self.onSnapshotToolClicked, self.snapshotTool)

		self.videoView.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)
		# cool hack: key event listener only works if the focus is in some elements like our videoview
		self.videoView.SetFocus()

		self._title=wx.StaticText(self.getTitlePanel(),label=_("Extrinsic calibration (Step 1): rotating plate calibration"))
		font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.FONTWEIGHT_BOLD,True)
		self._title.SetFont(font)
		self._subTitle=wx.StaticText(self.getTitlePanel(),label=_("Place the pattern adjusting it to the grid and let the scanner calibrate itself"))
		
		vbox=wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self._title,0,wx.LEFT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 10)	
		vbox.Add(self._subTitle,0,wx.LEFT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 10)	
		
		self.getTitlePanel().SetSizer(vbox)
		self.Layout()
		self.ghbox = wx.BoxSizer(wx.HORIZONTAL)
		self.ghbox.Add(self,1,wx.EXPAND,0)
		self.parent.SetSizer(self.ghbox)

		self.parent.parent.Layout()
	def onPlayToolClicked(self, event):
		
		self.scanner.connect()
		self.timer.Start(milliseconds=150)
		self.guideView.setFrame()

	def onSnapshotToolClicked(self, event):
		
		frame = self.scanner.camera.captureImage(False)
		self.addToGrid(frame)

	def onTimer(self, event):
		frame = self.scanner.camera.captureImage(True)
		self.videoView.setFrame(frame)

	def OnKeyPress(self,event):
		if not self.loaded:
			self.scanner.connect()
			self.timer.Start(milliseconds=150)
			self.loaded=True
			self.start(0)
			print event.GetKeyCode()
		elif event.GetKeyCode()==32:
			frame = self.scanner.camera.captureImage(True)
			self.addToGrid(frame)
	def start(self,event):
		self.guideView.Show(False)
		self.getRightButton().Bind(wx.EVT_BUTTON,self.parent.parent.loadInit)
		self.plot2DPanel=wx.Panel(self._upPanel, id=wx.ID_ANY,style=wx.SUNKEN_BORDER)
		
		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.videoView,2,wx.EXPAND|wx.ALL,1)
		

		self.fig = Figure(facecolor='white')
		self.canvas = FigureCanvasWxAgg( self.plot2DPanel, -1, self.fig)
		self.ax = self.fig.gca()
		self.ax.axis('equal')
		
		self.x2D=np.array([])
		self.z2D=np.array([])
		self.plot2DPanel.Bind(wx.EVT_SIZE, self.on_size)

		hbox.Add(self.plot2DPanel,5,wx.EXPAND|wx.ALL,1)
		self._upPanel.SetSizer(hbox)

		self.parent.Layout()
		self.plot()

	def plot(self):
		self.ax.cla()
		
		transVectors=np.array( [np.array([[ -42.69884629],
			   [ -60.66166513],
			   [ 321.66039025]]), np.array([[ -42.41493766],
			   [ -60.64227845],
			   [ 314.83533902]]),np.array([[ -41.50678247],
			   [ -60.61090239],
			   [ 309.86558147]]), np.array([[ -39.94829325],
			   [ -60.53994931],
			   [ 304.62751714]]), np.array([[ -35.74329096],
			   [ -60.37072737],
			   [ 295.90780527]]), np.array([[ -28.6653856 ],
			   [ -60.11288896],
			   [ 287.22736507]]), np.array([[ -17.04165965],
			   [ -59.83398485],
			   [ 280.00927257]]), np.array([[  -7.25630751],
			   [ -59.66790518],
			   [ 277.30374209]]), np.array([[   2.22381082],
			   [ -59.49892478],
			   [ 276.60780411]])])
		
		
		self.x2D=np.array([])
		self.z2D=np.array([])
		for transUnit in transVectors:
			   self.x2D=np.hstack((self.x2D,transUnit[0][0]))
			   self.z2D=np.hstack((self.z2D,transUnit[2][0]))
		self.x2D=np.r_[self.x2D]
		self.z2D=np.r_[self.z2D]
		center_estimate = 0, 310
		print center_estimate
		center, ier = optimize.leastsq(self.f, center_estimate)

		self.xc, self.zc = center

		Ri     = self.calc_R(*center)
		self.R      = Ri.mean()
		residu = sum((Ri - self.R)**2)

		print self.xc,self.zc
		print self.R

		theta_fit = np.linspace(-np.pi, np.pi, 180)

		x_fit2 = self.xc + self.R*np.cos(theta_fit)
		z_fit2 = self.zc + self.R*np.sin(theta_fit)
		self.ax.plot(x_fit2, z_fit2, 'k--', lw=2)
		self.ax.plot([self.xc], [self.zc], 'gD', mec='r', mew=1)
		self.ax.set_xlabel('x')
		self.ax.set_ylabel('z')

		# plot the residu fields
		nb_pts = 100

		self.canvas.draw()
		xmin, xmax = self.ax.set_xlim()
		ymin, ymax = self.ax.set_ylim()

		vmin = min(xmin, ymin)
		vmax = max(xmax, ymax)

		xg, zg = np.ogrid[vmin-self.R:(vmin+4*self.R):nb_pts*1j, vmax-4*self.R:vmax+self.R:nb_pts*1j]
		xg = xg[..., np.newaxis]
		zg = zg[..., np.newaxis]

		Rig    = np.sqrt( (xg - self.x2D)**2 + (zg - self.z2D)**2 )
		Rig_m  = Rig.mean(axis=2)[..., np.newaxis]  
		residu = np.sum( (Rig-Rig_m)**2 ,axis=2)
		lvl = np.exp(np.linspace(np.log(residu.min()), np.log(residu.max()), 15))

		self.ax.contourf(xg.flat, zg.flat, residu.T, lvl, alpha=0.4, cmap=cm.Purples_r) # , norm=colors.LogNorm())
		
		self.ax.contour (xg.flat, zg.flat, residu.T, lvl, alpha=0.8, colors="lightblue")

		# plot data
		self.ax.plot(self.x2D, self.z2D, 'ro', label='data', ms=8, mec='b', mew=1)
		self.ax.legend(loc='best',labelspacing=0.1 )

		self.ax.set_xlim(xmin=(self.xc-self.R)*1.05, xmax=(self.xc+self.R)*1.05)
		self.ax.set_ylim(ymin=(self.zc-self.R)*1.05, ymax=(self.zc+self.R)*1.05)

		self.ax.grid()

		self.canvas.draw()


	def calc_R(self,xc, zc):
		return np.sqrt((self.x2D-xc)**2 + (self.z2D-zc)**2)

	def f(self,c):
		Ri = self.calc_R(*c)
		return Ri - Ri.mean()

	
	def on_size(self,event):
		pix = self.plot2DPanel.GetClientSize()
		self.fig.set_size_inches(pix[0]/self.fig.get_dpi(),pix[1]/self.fig.get_dpi())
		x,y = self.plot2DPanel.GetSize()  
		self.canvas.SetClientSize((x, y))
		self.ax.axis('equal')
		if hasattr(self,'xc'):
			self.ax.set_xlim(xmin=(self.xc-self.R)*1.05, xmax=(self.xc+self.R)*1.05)
			self.ax.set_ylim(ymin=(self.zc-self.R)/1.05, ymax=(self.zc+self.R)*1.05)
		self.canvas.draw()
		event.Skip()
	def hide(self):
		if hasattr(self,'canvas'):
			self.canvas.Show(False)
		self.Show(False)
		# self.getPanel().Unbind(wx.EVT_SIZE)
	def show(self):
		if hasattr(self,'canvas'):
			self.canvas.Show(True)
		self.Show(True)

class IntrinsicsPanel(wx.Panel):

	def __init__(self,parent,calibration):

		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY,style=wx.SUNKEN_BORDER)
		self.parent=parent
		self.calibration=calibration
		self._vCalMatrix= [["fx= ","","cx= "],["","fy= ","cy= "],["","",""]] # TODO connect with scanner's calibration matrix
		self._calMatrix=parent.parent.calibration._calMatrix
		self._calMatrixDefault=parent.parent.calibration._calMatrixDefault
		self._vDistortionVector=["k1=","k2=","p1=","p2=","k3="] 
		self._distortionVector=parent.parent.calibration._distortionVector
		self._distortionVectorDefault=parent.parent.calibration._distortionVectorDefault
		self._editControl=False  # True means editing state
		self.load()
		

	def load(self):

		# self.SetBackgroundColour((random.randrange(255),random.randrange(255),random.randrange(255)))
		# toolbar
		self._intrinsicTitle=wx.StaticText(self,label=_("Step 1: Intrinsic parameters"))
		font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL,True)
		
		self._intrinsicTitle.SetFont(font)

		vbox=wx.BoxSizer(wx.VERTICAL)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._intrinsicTitle,0,wx.ALL,20)
		hbox.Add((-1,-1),1)

		image1=wx.Bitmap(resources.getPathForImage("edit.png"))
		image1=self.scale_bitmap(image1,55,55)
		self._editButton = wx.BitmapButton(self, id=-1, bitmap=image1, size = (image1.GetWidth()+5, image1.GetHeight()+5))
		self._editButton.Bind(wx.EVT_BUTTON,self.edit)

		image2=wx.Bitmap(resources.getPathForImage("restore.png"))
		image2=self.scale_bitmap(image2,55,55)
		self._restoreButton = wx.BitmapButton(self, id=-1, bitmap=image2, size = (image2.GetWidth()+5, image2.GetHeight()+5))
		self._restoreButton.Bind(wx.EVT_BUTTON,self.restore)

		hbox.Add(self._editButton,0,wx.ALL,0)
		hbox.Add(self._restoreButton,0,wx.ALL,0)

		vboxAux=wx.BoxSizer(wx.VERTICAL)
		vboxAux.Add(hbox,0,wx.EXPAND | wx.ALL,0)

		vboxAux.Add(wx.StaticLine(self,wx.ID_ANY,(-1,-1),(-1,2)),1,wx.GROW | wx.ALL,0)

		vbox.Add(vboxAux,0,wx.EXPAND|wx.ALIGN_TOP,0)

		#camera matrix
		font = wx.Font(12, wx.SCRIPT, wx.NORMAL, wx.BOLD)
		self._camMatrixTitle=wx.StaticBox(self,label=_("Camera Matrix"))
		self._camMatrixTitle.SetFont(font)
		boxSizer = wx.StaticBoxSizer(self._camMatrixTitle,wx.HORIZONTAL)
		boxSizer.Add((-1,50),0,wx.ALL,5)

		self._visualMatrix=[[0 for j in range(len(self._vCalMatrix))] for i in range(len(self._vCalMatrix[0]))]
		self._visualCtrlMatrix=[[0 for j in range(len(self._visualMatrix))] for i in range(len(self._visualMatrix[0]))]
		
		for j in range(len(self._vCalMatrix[0])):
			vbox2 = wx.BoxSizer(wx.VERTICAL)  

			for i in range (len(self._vCalMatrix)):
				label=str(self._vCalMatrix[i][j]) + str(self._calMatrix[i][j])
			
				self._visualMatrix[i][j]= wx.StaticText(self,label=label)

				self._visualCtrlMatrix[i][j]=wx.TextCtrl(self,-1,str(self._calMatrix[i][j]))

				vbox2.Add(self._visualMatrix[i][j],0,wx.EXPAND|wx.ALL,20)
				
				vbox2.Add(self._visualCtrlMatrix[i][j],0,wx.EXPAND|wx.ALL,15)
				self._visualCtrlMatrix[i][j].Show(False)
			
			boxSizer.Add(vbox2,1,wx.EXPAND | wx.ALL,0)

		boxSizer.Add((-1,50),0,wx.ALL,5)

		vbox.Add(boxSizer,0,wx.EXPAND|wx.ALL,30)
		
		#distortion coefficients
		self._distortionCoeffStaticText = wx.StaticBox(self, label=_("Distortion coefficients"))
		self._distortionCoeffStaticText.SetFont(font)
		boxSizer = wx.StaticBoxSizer(self._distortionCoeffStaticText,wx.VERTICAL)

		vboxAux= wx.BoxSizer(wx.VERTICAL)
		self._visualDistortionVector=[0 for j in range(len(self._distortionVector))]
		self._visualCtrlDistortionVector=[0 for j in range(len(self._distortionVector))]
		for i in range(len(self._vDistortionVector)):
			label=str(self._vDistortionVector[i])+str(self._distortionVector[i])
			self._visualDistortionVector[i]=wx.StaticText(self,label=label)
			self._visualCtrlDistortionVector[i]=wx.TextCtrl(self,value=str(self._distortionVector[i]))
			vboxAux.Add( self._visualCtrlDistortionVector[i],0,wx.ALL|wx.EXPAND,14)
			self._visualCtrlDistortionVector[i].Show(False)
			vboxAux.Add( self._visualDistortionVector[i],0,wx.ALL|wx.EXPAND,20)

		boxSizer.Add(vboxAux,-1,wx.EXPAND,0)

		vbox.Add(boxSizer,0,wx.ALIGN_LEFT|wx.ALL|wx.EXPAND,30)

		#buttons
		self._startButton = wx.Button(self,label=_("Start"),size=(100,-1))
		self._startButton.Bind(wx.EVT_BUTTON,self.start)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._startButton,0,wx.ALL,20)
		
		vboxAux=wx.BoxSizer(wx.VERTICAL)
		

		vboxAux.Add(wx.StaticLine(self,wx.ID_ANY,(-1,-1),(-1,2)),1,wx.GROW | wx.ALL,0)
		vboxAux.Add(hbox,0,wx.EXPAND | wx.ALL,0)
		vbox.Add(vboxAux,0,wx.EXPAND|wx.ALIGN_TOP,0)

		self.SetSizer(vbox)
		
	def start(self,event):
		# print self.parent
		self.parent.parent.loadPagePattern(0)

	def restore(self,event):
		print "restore"
		for i in range(len(self._visualMatrix)):
			for j in range(len(self._visualMatrix[0])):

				self._calMatrix.itemset((i,j),self._calMatrixDefault[i][j])
				self._visualCtrlMatrix[i][j].SetValue(str(self._calMatrixDefault[i][j]))
				label=str(self._vCalMatrix[i][j]) + str(self._calMatrix[i][j])
		
				self._visualMatrix[i][j].SetLabel(label)
		for i in range(len(self._vDistortionVector)):
			
			self._distortionVector.itemset((i),self._distortionVectorDefault[i])
			self._visualCtrlDistortionVector[i].SetValue(str(self._distortionVectorDefault[i]))
			label=str(self._vDistortionVector[i])+str(self._distortionVector[i])
			self._visualDistortionVector[i].SetLabel(label)

			
		self.Layout()

	def edit(self,event):
		print "edit"
		if self._editControl:
			for i in range(len(self._visualMatrix)):
				for j in range(len(self._visualMatrix[0])):
					
					self._visualCtrlMatrix[i][j].Show(False)
					self._visualMatrix[i][j].Show(True)
					self._editControl=False
					self._calMatrix.itemset((i,j),self._visualCtrlMatrix[i][j].GetValue())
					label=str(self._vCalMatrix[i][j]) + str(self._calMatrix[i][j])
			
					self._visualMatrix[i][j].SetLabel(label)
			for i in range(len(self._vDistortionVector)):
				
				self._visualDistortionVector[i].Show(True)
				self._visualCtrlDistortionVector[i].Show(False)
				self._distortionVector.itemset((i),self._visualCtrlDistortionVector[i].GetValue())
				label=str(self._vDistortionVector[i])+str(self._distortionVector[i])
				self._visualDistortionVector[i].SetLabel(label)

			
			self.Layout()
		else:
			for i in range(len(self._visualMatrix)):
				for j in range(len(self._visualMatrix[0])):
					
					self._visualCtrlMatrix[i][j].Show(True)
					self._visualMatrix[i][j].Show(False)
					self._editControl=True
					
			for i in range(len(self._vDistortionVector)):
				self._visualDistortionVector[i].Show(False)
				self._visualCtrlDistortionVector[i].Show(True)
			self.Layout()
				
	def save(self,event):
		print "save"
	def scale_bitmap(self,bitmap, width, height):
		image = wx.ImageFromBitmap(bitmap)
		image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
		result = wx.BitmapFromImage(image)
		return result
	def reload(self):
		self._calMatrix=self.calibration._calMatrix
		self._distortionVector=self.calibration._distortionVector
		for i in range(len(self._visualMatrix)):
			for j in range(len(self._visualMatrix[0])):

				self._visualCtrlMatrix[i][j].SetValue(str(self._calMatrix[i][j]))
				label=str(self._vCalMatrix[i][j]) + str(self._calMatrix[i][j])
				self._visualMatrix[i][j].SetLabel(label)

		for i in range(len(self._vDistortionVector)):
			
			self._visualCtrlDistortionVector[i].SetValue(str(self._distortionVector[i]))
			label=str(self._vDistortionVector[i])+str(self._distortionVector[i])
			self._visualDistortionVector[i].SetLabel(label)	
		self.Layout()

class ExtrinsicsPanel(wx.Panel):

	def __init__(self,parent,calibration):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY,style=wx.SUNKEN_BORDER)
		self.parent=parent
		self.calibration=calibration
		self._vRotMatrix= [["r11=","r12=","r13="],["r21=","r22=","r23="],["r31=","r32=","r33="]] # TODO connect with scanner's calibration matrix
		self._rotMatrix=parent.parent.calibration._rotMatrix
		self._rotMatrixDefault=parent.parent.calibration._rotMatrixDefault

		self._vTransMatrix= [["t1="],["t2="],["t3="]] # TODO connect with scanner's calibration matrix
		self._transMatrix=parent.parent.calibration._transMatrix
		self._transMatrixDefault=parent.parent.calibration._transMatrixDefault
		self._editControl=False

		self.load()
	def load(self):
		# self.SetBackgroundColour((random.randrange(255),random.randrange(255),random.randrange(255)))
		self.SetBackgroundColour((255,255,255))
		self._extrinsicTitle=wx.StaticText(self,label=_("Step 2: Extrinsic parameters"))
		font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL,True)
		
		self._extrinsicTitle.SetFont(font)

		vbox=wx.BoxSizer(wx.VERTICAL)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._extrinsicTitle,0,wx.ALL,20)
		hbox.Add((-1,-1),1)

		image1=wx.Bitmap(resources.getPathForImage("edit.png"))
		image1=self.scale_bitmap(image1,55,55)
		self._editButton = wx.BitmapButton(self, id=-1, bitmap=image1, size = (image1.GetWidth()+5, image1.GetHeight()+5))
		self._editButton.Bind(wx.EVT_BUTTON,self.edit)

		image2=wx.Bitmap(resources.getPathForImage("restore.png"))
		image2=self.scale_bitmap(image2,55,55)
		self._restoreButton = wx.BitmapButton(self, id=-1, bitmap=image2, size = (image2.GetWidth()+5, image2.GetHeight()+5))
		self._restoreButton.Bind(wx.EVT_BUTTON,self.restore)

		hbox.Add(self._editButton,0,wx.ALL,0)
		hbox.Add(self._restoreButton,0,wx.ALL,0)

		vboxAux=wx.BoxSizer(wx.VERTICAL)
		vboxAux.Add(hbox,0,wx.EXPAND | wx.ALL,0)

		vboxAux.Add(wx.StaticLine(self,wx.ID_ANY,(-1,-1),(-1,2)),1,wx.GROW | wx.ALL,0)

		vbox.Add(vboxAux,0,wx.EXPAND|wx.ALIGN_TOP,0)

		#camera matrix
		font = wx.Font(12, wx.SCRIPT, wx.NORMAL, wx.BOLD)
		self.transMatrixTitle=wx.StaticBox(self,label=_("Translation Matrix"))
		self.transMatrixTitle.SetFont(font)
		boxSizer = wx.StaticBoxSizer(self.transMatrixTitle,wx.HORIZONTAL)
		boxSizer.Add((-1,50),0,wx.ALL,5)

		self._visualMatrix=[[0 for j in range(len(self._vRotMatrix)+1)] for i in range(len(self._vRotMatrix[0]))]
		self._visualCtrlMatrix=[[0 for j in range(len(self._vRotMatrix)+1)] for i in range(len(self._vRotMatrix[0]))]
		
		for j in range(len(self._vRotMatrix[0])):
			vbox2 = wx.BoxSizer(wx.VERTICAL)  
			for i in range (len(self._vRotMatrix)):
				label=str(self._vRotMatrix[i][j])+ str(self._rotMatrix[i][j])
				self._visualCtrlMatrix[i][j]=wx.TextCtrl(self,-1,str(self._rotMatrix[i][j]))
				
				self._visualMatrix[i][j]= wx.StaticText(self,label=label)
				vbox2.Add(self._visualMatrix[i][j],0,wx.ALL,20)
				vbox2.Add(self._visualCtrlMatrix[i][j],0,wx.EXPAND | wx.ALL,15)
				self._visualCtrlMatrix[i][j].Show(False)
			boxSizer.Add(vbox2,1,wx.EXPAND | wx.ALL,0)

		vbox2 = wx.BoxSizer(wx.VERTICAL)
		for j in range(len(self._vTransMatrix)):
			print self._vTransMatrix
			label=str(self._vTransMatrix[j][0])+ str(self._transMatrix[j][0])
			self._visualCtrlMatrix[j][3]=wx.TextCtrl(self,-1,str(self._transMatrix[j][0]))
				
			self._visualMatrix[j][3]= wx.StaticText(self,label=label)
			self._visualCtrlMatrix[j][3].Show(False)
			vbox2.Add(self._visualCtrlMatrix[j][3],0,wx.EXPAND | wx.ALL,15)
			vbox2.Add(self._visualMatrix[j][3],0,wx.ALL,20)
		boxSizer.Add(vbox2,1,wx.EXPAND | wx.ALL,0)
		


		boxSizer.Add((-1,50),0,wx.ALL,5)

		vbox.Add(boxSizer,0,wx.EXPAND|wx.ALL,30)
		

		#buttons
		self._startButton = wx.Button(self,label=_("Start"),size=(100,-1))
		self._startButton.Bind(wx.EVT_BUTTON,self.start)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._startButton,0,wx.ALL,20)
		
		vboxAux=wx.BoxSizer(wx.VERTICAL)
		

		vboxAux.Add(wx.StaticLine(self,wx.ID_ANY,(-1,-1),(-1,2)),1,wx.GROW | wx.ALL,0)
		vboxAux.Add(hbox,0,wx.EXPAND | wx.ALL,0)
		vbox.Add(vboxAux,0,wx.EXPAND,0)

		self.SetSizer(vbox)

	def start(self,event):
		self.parent.parent.loadExtrinsicCalibrationPanel(0)
	def restore(self,event):
		print "restore"
		for i in range(len(self._visualMatrix)):
			for j in range(len(self._visualMatrix[0])-1):

				self._rotMatrix.itemset((i,j),self._rotMatrixDefault[i][j])
				self._visualCtrlMatrix[i][j].SetValue(str(self._rotMatrixDefault[i][j]))
				label=str(self._vRotMatrix[i][j]) + str(self._rotMatrix[i][j])
		
				self._visualMatrix[i][j].SetLabel(label)
		for j in range(len(self._vTransMatrix)):
			
			self._transMatrix.itemset((j),self._transMatrixDefault[j])
			print j
			self._visualCtrlMatrix[j][3].SetValue(str(self._transMatrixDefault[j][0]))
			label=str(self._vTransMatrix[j][0])+str(self._transMatrix[j][0])
			self._visualMatrix[j][3].SetLabel(label)

			
			self.Layout()

	def edit(self,event):
		print "edit"
		if self._editControl:
			for i in range(len(self._visualMatrix)):
				for j in range(len(self._visualMatrix[0])-1):
					
					self._visualCtrlMatrix[i][j].Show(False)
					self._visualMatrix[i][j].Show(True)
					self._editControl=False
					self._rotMatrix.itemset((i,j),self._visualCtrlMatrix[i][j].GetValue())
					
					label=str(self._vRotMatrix[i][j]) + str(self._rotMatrix[i][j])
			
					self._visualMatrix[i][j].SetLabel(label)
			for j in range(len(self._vTransMatrix)):
				
				self._visualMatrix[j][3].Show(True)
				self._visualCtrlMatrix[j][3].Show(False)
				self._transMatrix.itemset((j),self._visualCtrlMatrix[j][3].GetValue())
				label=str(self._vTransMatrix[j][0])+str(self._transMatrix[j][0])
				self._visualMatrix[j][3].SetLabel(label)


			
			self.Layout()
		else:
			for i in range(len(self._visualMatrix)):
				for j in range(len(self._visualMatrix[0])):
					
					self._visualCtrlMatrix[i][j].Show(True)
					self._visualMatrix[i][j].Show(False)
					self._editControl=True
					
			
			self.Layout()

	def save(self,event):
		print "save"

	def scale_bitmap(self,bitmap, width, height):
		image = wx.ImageFromBitmap(bitmap)
		image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
		result = wx.BitmapFromImage(image)
		return result
