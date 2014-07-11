#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: June 2014                                                       #
# Author: Carlos Crespo <carlos.crespo@bq.com   	                    #
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

import wx.lib.scrolledpanel

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

import matplotlib.cm as cm  
import matplotlib.colors as colors

class CalibrationWorkbench(Workbench):

	def __init__(self, parent):
		Workbench.__init__(self, parent, 1, 1)
		self.parent=parent
		self.scanner = self.GetParent().scanner
		self.calibration = self.GetParent().calibration
		self.load()

	def load(self):

		#-- Toolbar Configuration

		self.connectTool       = self.toolbar.AddLabelTool(wx.NewId(), _("Connect"), wx.Bitmap(getPathForImage("connect.png")), shortHelp=_("Connect"))
		self.disconnectTool    = self.toolbar.AddLabelTool(wx.NewId(), _("Disconnect"), wx.Bitmap(getPathForImage("disconnect.png")), shortHelp=_("Disconnect"))
		
		#-- Disable Toolbar Items

		self.enableLabelTool(self.connectTool      , True)
		self.enableLabelTool(self.disconnectTool   , False)
		
		#-- Bind Toolbar Items

		self.Bind(wx.EVT_TOOL, self.onConnectToolClicked      , self.connectTool)
		self.Bind(wx.EVT_TOOL, self.onDisconnectToolClicked   , self.disconnectTool)
		
		self.toolbar.Realize()

		self._panel.parent=self
		self._intrinsicsPanel=IntrinsicsPanel(self._panel,self.calibration)
		self._extrinsicsPanel=ExtrinsicsPanel(self._panel,self.calibration)

		self.setLayout()

	def loadInit(self,event):
		
		if hasattr(self,'_extrinsicCalibrationPanel'):
			self._extrinsicCalibrationPanel.hide()
		if hasattr(self,'_patternPanel'):
			self._patternPanel.loaded=False
			self._patternPanel.Show(False)
			self._patternPanel.setLayout()
			if self._patternPanel.timer.IsRunning:
				self._patternPanel.timer.Stop()
				self._patternPanel.videoView.setImage(wx.Image(getPathForImage("bq.png")))
		if hasattr(self,'_plotPanel'):
			self._plotPanel.hide()
		self._intrinsicsPanel.Show(True)
		self._intrinsicsPanel.reload()
		self._extrinsicsPanel.Show(True)
		self._extrinsicsPanel.reload()
		self.setLayout()

	def loadPagePattern(self,event):
		self._intrinsicsPanel.Show(False)
		self._extrinsicsPanel.Show(False)
		if not hasattr(self,'_patternPanel'):
			self._patternPanel=PatternPanel(self._panel,self.scanner,self.calibration)			
		else:
			self._patternPanel.Show(True)
			self._patternPanel.clear()
			self._patternPanel.setLayout()
			self._patternPanel.videoView.SetFocus()

	def loadPagePlot(self,event):
		self._patternPanel.Show(False)
		if not hasattr(self,'_plotPanel'):
			self._plotPanel=PlotPanel(self._panel,self.calibration)
		else:
			self._plotPanel.reload()
			self._plotPanel.show()
			self._plotPanel.setLayout()
	
	def loadExtrinsicCalibrationPanel(self,event):
		self._intrinsicsPanel.Show(False)
		self._extrinsicsPanel.Show(False)

		if not hasattr(self,'_extrinsicCalibrationPanel'):
			self._extrinsicCalibrationPanel=ExtrinsicCalibrationPanel(self._panel,self.scanner,self.calibration)
		else:
			self._extrinsicCalibrationPanel.Show(True)
			self._extrinsicCalibrationPanel.guideView.Show(True)
			self._extrinsicCalibrationPanel.videoView.SetFocus()
			self._extrinsicCalibrationPanel.getRightButton().Bind(wx.EVT_BUTTON,self._extrinsicCalibrationPanel.start)
			self._extrinsicCalibrationPanel.setLayout()

	def setLayout(self):
		self.initHbox = wx.BoxSizer(wx.HORIZONTAL)

		self.initHbox.Add(self._intrinsicsPanel,1,wx.EXPAND|wx.ALL,10)
		self.initHbox.Add(self._extrinsicsPanel,1,wx.EXPAND|wx.ALL,10)
		self._panel.SetSizer(self.initHbox)
		self.Layout()

	def enableLabelTool(self, item, enable):
		self.toolbar.EnableTool(item.GetId(), enable)

	def onConnectToolClicked(self, event):
		self.enableLabelTool(self.disconnectTool,True)
		self.enableLabelTool(self.connectTool,False)
		self.scanner.connect()

	def onDisconnectToolClicked(self, event):
		self.scanner.disconnect() # Not working camera disconnect :S

		# TODO: Check disconnection
		self.enableLabelTool(self.connectTool, True)
		self.enableLabelTool(self.disconnectTool,False)
		self.loadInit(0)
		
class PatternPanel(Page):
	def __init__(self,parent,scanner,calibration):
		Page.__init__(self,parent)
		self.parent=parent;
		
		self.scanner=scanner
		self.calibration=calibration
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
		self.getLeftButton().Bind(wx.EVT_BUTTON,self.parent.parent.loadInit)
		self.getLeftButton().SetLabel("Cancel")
		self.getRightButton().Bind(wx.EVT_BUTTON,self.calibrateCamera)
		self.getRightButton().SetLabel("Calibrate!")
		self.getRightButton().Disable()
		self.loaded=False
		self.currentGrid=0
		# set quantity of photos to take
		self.rows=2
		self.columns=6
		self.load() 
	def load(self):

		self.videoView = VideoView(self._upPanel)
		self.guideView = VideoView(self._upPanel)
		

		self.videoView.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)
		# cool hack: key event listener only works if the focus is in some elements like our videoview
		self.videoView.SetFocus()

		# be sure that the focus is always where it should be

		self.Bind(wx.EVT_SET_FOCUS,self.returnFocus)
		self._titlePanel.Bind(wx.EVT_SET_FOCUS,self.returnFocus)
		self._upPanel.Bind(wx.EVT_SET_FOCUS,self.returnFocus)
		self._downPanel.Bind(wx.EVT_SET_FOCUS,self.returnFocus)
		self.getLeftButton().Bind(wx.EVT_SET_FOCUS,self.returnFocus)
		self.getRightButton().Bind(wx.EVT_SET_FOCUS,self.returnFocus)
		self.parent.parent.parent.comboBoxWorkbench.Bind(wx.EVT_SET_FOCUS,self.returnFocus)

		self._title=wx.StaticText(self.getTitlePanel(),label=_("Intrinsic calibration (Step 1): camera calibration"))
		font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.FONTWEIGHT_BOLD,True)
		self._title.SetFont(font)
		self._subTitle=wx.StaticText(self.getTitlePanel(),label=_("Place the pattern adjusting it to the grid"))
		
		vbox=wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self._title,0,wx.LEFT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 10)	
		vbox.Add(self._subTitle,0,wx.LEFT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 10)	
		
		
		self.getTitlePanel().SetSizer(vbox)
		self.setLayout()
		
	def returnFocus(self,event):
		self.videoView.SetFocus()

	def onTimer(self, event):
		frame = self.scanner.camera.captureImage(True)
		frame=self.calibration.undistortImage(frame)
		self.videoView.setFrame(frame)


	def OnKeyPress(self,event):
		"""Key bindings: if it is not started, spacebar initialize the scanner"""
		if not self.loaded:
			if not self.scanner.isConnected:
				self.scanner.connect()

			self.timer.Start(milliseconds=150)
			self.loaded=True
			self.loadGrid()
			
		elif event.GetKeyCode()==32:
			frame = self.scanner.camera.captureImage(False)
			frame,retval= self.calibration.detectPrintChessboard(frame)
			self.addToGrid(frame,retval)
		
	def loadGrid(self):
		self.guideView.Show(False)
		if not hasattr(self,'gridPanel'):
			self.gridPanel=wx.Panel(self._upPanel, id=wx.ID_ANY)
			
			gs=wx.GridSizer(self.rows,self.columns,3,3)
			self.panelGrid=[]
			for panel in range(self.rows*self.columns):
				self.panelGrid.append(VideoView(self.gridPanel))
				self.panelGrid[panel].SetBackgroundColour((random.randrange(255),random.randrange(255),random.randrange(255)))	
				self.panelGrid[panel].index=panel
				gs.Add(self.panelGrid[panel],0,wx.EXPAND)
				self.panelGrid[panel].Bind(wx.EVT_LEFT_DOWN,self.onClick)
			self.gridPanel.SetSizer(gs)
		else:
			self.gridPanel.Show(True)
			self.clear()
		hbox= wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.videoView,2,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.gridPanel,5,wx.EXPAND|wx.ALL,1)
		self._upPanel.SetSizer(hbox)
		self._upPanel.Layout()
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
		if self.currentGrid is (self.columns*self.rows):
			self.getRightButton().Enable()	

	def clear(self):
		if hasattr(self,'panelGrid'):
			for panel in self.panelGrid:
				panel.setImage(wx.Image(getPathForImage("bq.png")))
				panel.SetBackgroundColour((random.randrange(255),random.randrange(255),random.randrange(255)))	
			
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
		self.timer.Stop()
		self.videoView.setImage(wx.Image(getPathForImage("bq.png")))
		self.loaded=False

	def setLayout(self):
		hbox= wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.videoView,2,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.guideView,5,wx.EXPAND|wx.ALL,1)

		self._upPanel.SetSizer(hbox)
		self.ghbox = wx.BoxSizer(wx.HORIZONTAL)
		self.ghbox.Add(self,1,wx.EXPAND,0)
		self.parent.SetSizer(self.ghbox)
		
		if hasattr(self,'gridPanel'):
			self.gridPanel.Show(False)
		if hasattr(self,'guideView'):
			self.guideView.Show(True)
			self.videoView.Show(True)
			
		if self.scanner.isConnected:
			self.showSpaceHelp()	
		else:
			self.showSocketHelp()
		self.parent.parent.Bind(wx.EVT_TOOL, self.onDisconnectToolClicked   , self.parent.parent.disconnectTool)
		self._upPanel.Layout()
		self.parent.Layout()

	def showSpaceHelp(self):
		self.guideView.setImage(wx.Image(getPathForImage("keyboard.png")))
		if hasattr(self,'text'):
			self.text.SetLabel(_("Press the space bar to perform captures"))
		else:
			self.text=wx.StaticText(self.guideView,label=_("Press the space bar to perform captures. Press space to start taking captures."))	
	
	def showSocketHelp(self):
		self.guideView.setImage(wx.Image(getPathForImage("socket.png")))
		if hasattr(self,'text'):
			self.text.SetLabel(_("Please connect the scanner"))
		else:
			self.text=wx.StaticText(self.guideView,label=_("Please connect the scanner"))		
		self.parent.parent.Bind(wx.EVT_TOOL , self.onConnectToolClicked,self.parent.parent.connectTool)
	
	def onConnectToolClicked(self,event):
		self.parent.parent.enableLabelTool(self.parent.parent.disconnectTool,True)
		self.parent.parent.enableLabelTool(self.parent.parent.connectTool,False)
		self.scanner.connect()
		self.showSpaceHelp()
	def onDisconnectToolClicked(self,event):
		
		self.scanner.disconnect() # Not working camera disconnect :S

		# TODO: Check disconnection
		self.parent.parent.enableLabelTool(self.parent.parent.connectTool, True)
		self.parent.parent.enableLabelTool(self.parent.parent.disconnectTool,False)
		self.parent.parent.loadInit(0)
		
class PlotPanel(Page):
	def __init__(self,parent,calibration):
		Page.__init__(self,parent)
		self.calibration=calibration
		self.parent=parent;
		self.getLeftButton().Bind(wx.EVT_BUTTON,self.rejectCalibration)
		self.getLeftButton().SetLabel(_("Reject"))
		self.getRightButton().Bind(wx.EVT_BUTTON,self.acceptCalibration)
		self.getRightButton().SetLabel(_("Accept"))
		self.scaleFactor=3*80
		self.load()
	def load(self):
		

		self.fig = Figure(tight_layout=True)
		self.canvas = FigureCanvasWxAgg( self.getPanel(), -1, self.fig)
		self.canvas.SetExtraStyle(wx.EXPAND)

		self.ax = self.fig.gca(projection='3d',axisbg=(random.random(),random.random(),random.random()))
		self.getPanel().Bind(wx.EVT_SIZE, self.on_size)
		# Parameters of the pattern
		self.columns=self.calibration.patternColumns+2
		self.rows=self.calibration.patternRows+2
		self.squareWidth=self.calibration.squareWidth
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
		
		self.printCanvas()
		
		self._title=wx.StaticText(self.getTitlePanel(),label=_("Intrinsic calibration (Step 2): plot "))
		font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.FONTWEIGHT_BOLD,True)
		self._title.SetFont(font)
		self._subTitle=wx.StaticText(self.getTitlePanel(),label=_("Here you can see the plot, please, accept or reject the calibration"))
		
		vbox=wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self._title,0,wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 1)	
		vbox.Add(self._subTitle,0,wx.TOP|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 10)	
		
		self.getTitlePanel().SetSizer(vbox)
		
		self.matrixPanel=wx.lib.scrolledpanel.ScrolledPanel( parent=self.getPanel(), id=wx.ID_ANY)
		
		vbox=wx.BoxSizer(wx.VERTICAL)
		self.loadMatrices(self.matrixPanel,vbox)
		self.matrixPanel.SetSizer(vbox)
		self.getPanel().Bind(wx.EVT_SIZE, self.on_size)
		self.setLayout()
		

	def on_size(self,event):
		factor=1
		# pix = self.getPanel().GetClientSize()
		# self.fig.set_size_inches(pix[0]/self.fig.get_dpi(),pix[1]/self.fig.get_dpi())
		x,y = self.getPanel().GetSize()  
		self.canvas.SetClientSize((y*factor, y))
		# self.ax.set_xlim(-150, 150)
		# self.ax.set_ylim(0, 300)
		# self.ax.set_zlim(-150/factor, 150/factor)
		# self.ax.invert_xaxis()
		# self.ax.invert_yaxis()
		# self.ax.invert_zaxis()
		# self.canvas.draw()
		self.reloadMatrix()
		self._upPanel.Layout()
		self.Layout()
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
		self.addToCanvas()

	def addToCanvas(self):
		self.rotation=self.calibration.rvecs
		self.translation=self.calibration.tvecs
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
		self.reloadMatrix()


	def setLayout(self):
		self.initHbox = wx.BoxSizer(wx.HORIZONTAL)

		self.initHbox.Add(self.canvas,1,wx.EXPAND|wx.ALL,10)
		self.initHbox.Add(self.matrixPanel,1,wx.EXPAND|wx.ALL,10)
		self._upPanel.SetSizer(self.initHbox)
		self.Layout()
		self.ghbox = wx.BoxSizer(wx.HORIZONTAL)
		self.ghbox.Add(self,1,wx.EXPAND|wx.ALL,10)
		self.parent.SetSizer(self.ghbox)
		self.parent.Layout()
	def acceptCalibration(self,event):
		self.calibration.saveCalibrationMatrix()
		self.calibration.saveDistortionVector()
		self.parent.parent.loadInit(0)

	def rejectCalibration(self,event):
		self.calibration.updateProfileToAllControls()
		self.parent.parent.loadInit(0)

	def loadMatrices(self,parent,sizer):
		#camera matrix
		font = wx.Font(12, wx.SCRIPT, wx.NORMAL, wx.BOLD)
		self._camMatrixTitle=wx.StaticBox(parent,label=_("Camera Matrix"))
		self._camMatrixTitle.SetFont(font)
		boxSizer = wx.StaticBoxSizer(self._camMatrixTitle,wx.HORIZONTAL)
		boxSizer.Add((-1,50),0,wx.ALL,5)
		self._visualMatrix=[[0 for j in range(len(self.parent.parent._intrinsicsPanel._vCalMatrix))] for i in range(len(self.parent.parent._intrinsicsPanel._vCalMatrix[0]))]
		
		for j in range(len(self.parent.parent._intrinsicsPanel._vCalMatrix[0])):
			vbox2 = wx.BoxSizer(wx.VERTICAL)  
			for i in range (len(self.parent.parent._intrinsicsPanel._vCalMatrix)):
				label=str(self.parent.parent._intrinsicsPanel._vCalMatrix[i][j]) + str(self.calibration._calMatrix[i][j])
				self._visualMatrix[i][j]= wx.StaticText(parent,label=label)
				vbox2.Add(self._visualMatrix[i][j],0,wx.EXPAND|wx.TOP,27)
			boxSizer.Add(vbox2,1,wx.EXPAND | wx.ALL,5)

		boxSizer.Add((-1,50),0,wx.ALL,5)
		sizer.Add(boxSizer,0,wx.EXPAND|wx.ALL,30)
		
		#distortion coefficients
		self._distortionCoeffStaticText = wx.StaticBox(parent, label=_("Distortion coefficients"))
		self._distortionCoeffStaticText.SetFont(font)
		boxSizer = wx.StaticBoxSizer(self._distortionCoeffStaticText,wx.VERTICAL)

		vboxAux= wx.BoxSizer(wx.VERTICAL)
		hboxRow1=wx.BoxSizer(wx.HORIZONTAL)
		hboxRow2=wx.BoxSizer(wx.HORIZONTAL)
		self._visualDistortionVector=[0 for j in range(len(self.calibration._distortionVector))]
		for i in range(len(self.parent.parent._intrinsicsPanel._vDistortionVector)):		
			label=str(self.parent.parent._intrinsicsPanel._vDistortionVector[i])+str(self.calibration._distortionVector[i])
			self._visualDistortionVector[i]=wx.StaticText(parent,label=label)
			if i<3:	
				hboxRow1.Add( self._visualDistortionVector[i],1,wx.ALL|wx.EXPAND,5)
			else:
				hboxRow2.Add( self._visualDistortionVector[i],1,wx.ALL|wx.EXPAND,5)
		hboxRow2.Add( (-1,-1),1,wx.ALL|wx.EXPAND,5)
		vboxAux.Add(hboxRow1,0,wx.EXPAND|wx.TOP,15)
		vboxAux.Add(hboxRow2,0,wx.EXPAND|wx.TOP,15)
		boxSizer.Add(vboxAux,-1,wx.EXPAND,0)

		sizer.Add(boxSizer,0,wx.ALIGN_LEFT|wx.ALL|wx.EXPAND,30)

	def reloadMatrix(self):
		x,_= self.GetClientSize()
		optimalTrimming=x/(self.scaleFactor)
		self._trimmedCalMatrix=np.around(np.copy(self.calibration._calMatrix),decimals=optimalTrimming)
		self._trimmedDistortionVector=np.around(np.copy(self.calibration._distortionVector),decimals=optimalTrimming)
		
		for i in range(len(self.parent.parent._intrinsicsPanel._visualMatrix)):
			for j in range(len(self.parent.parent._intrinsicsPanel._visualMatrix[0])):

				label=str(self.parent.parent._intrinsicsPanel._vCalMatrix[i][j]) + str(self._trimmedCalMatrix[i][j])
				self._visualMatrix[i][j].SetLabel(label)

		for i in range(len(self.parent.parent._intrinsicsPanel._vDistortionVector)):
			
			label=str(self.parent.parent._intrinsicsPanel._vDistortionVector[i])+str(self._trimmedDistortionVector[i])
			self._visualDistortionVector[i].SetLabel(label)	
		
		self.Layout()
		
class ExtrinsicCalibrationPanel(Page):
	def __init__(self,parent,scanner,calibration):
		Page.__init__(self,parent)
		self.scanner=scanner
		self.parent=parent
		self.calibration=calibration
		self.timer = wx.Timer(self)
		self.calibrationTimer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
		self.Bind(wx.EVT_TIMER, self.onCalibrationTimer, self.calibrationTimer)
		self.getLeftButton().Bind(wx.EVT_BUTTON,self.parent.parent.loadInit)
		self.getLeftButton().SetLabel(_("Cancel"))
		self.getRightButton().Bind(wx.EVT_BUTTON,self.start)
		self.getRightButton().SetLabel(_("Next"))
		self.getRightButton().Disable()
		self.loaded=False
		self.load()

		self.workingOnExtrinsic=True
		self.isFirstPlot=True
		self.stopExtrinsicSamples=40

	def load(self):
		self.videoView = VideoView(self._upPanel)
		self.guideView = VideoView(self._upPanel)
		hbox= wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.videoView,2,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.guideView,5,wx.EXPAND|wx.ALL,1)
		
		self._upPanel.SetSizer(hbox)

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
		
		self.setLayout()
	

	def onTimer(self, event):
		frame = self.scanner.camera.captureImage(True)
		self.videoView.setFrame(frame)

	def onCalibrationTimer(self,event):
		frame = self.scanner.camera.captureImage(False)
		self.scanner.device.setMotorCCW()
		
		self.addToPlot(frame)
		if len(self.calibration.transVectors)> self.stopExtrinsicSamples:
			self.calibrationTimer.Stop()
			self.getLeftButton().SetLabel(_("Reject"))
			self.getLeftButton().Bind(wx.EVT_BUTTON,self.parent.parent.loadInit)
		
			self.getRightButton().Bind(wx.EVT_BUTTON,self.acceptCalibration)	
			self.getRightButton().SetLabel(_("Accept"))
			self.getRightButton().Enable()

	def OnKeyPress(self,event):
		if not self.loaded:
			self.scanner.connect()
			self.timer.Start(milliseconds=150)
			self.calibrationTimer.Start(milliseconds=500)
			self.loaded=True
			self.start(0)
			
		elif event.GetKeyCode()==32:
			frame = self.scanner.camera.captureImage(True)
			self.scanner.device.setMotorCCW()
			
			self.addToPlot(frame)

	def addToPlot(self,image):
		retval=self.calibration.solvePnp(image)
		if (retval and (len(self.calibration.transVectors)>1)):
			self.plot()			
		else:
			print "Pattern not found"

	def start(self,event):
		self.guideView.Show(False)
		self.getRightButton().Bind(wx.EVT_BUTTON,self.parent.parent.loadInit)
		self.plot2DPanel=wx.Panel(self._upPanel, id=wx.ID_ANY)
		
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

		self.ax.set_xlabel('x')
		self.ax.set_ylabel('z')
		self.timer.Start(milliseconds=150)
		self.calibrationTimer.Start(milliseconds=500)
		self.loaded=True
		self.getRightButton().Disable()

	def plot(self):


		transVectors=self.calibration.transVectors
		
		self.x2D=np.array([])
		self.z2D=np.array([])
		for transUnit in transVectors:
			self.x2D=np.hstack((self.x2D,transUnit[0][0]))
			self.z2D=np.hstack((self.z2D,transUnit[2][0]))
		
		self.x2D=np.r_[self.x2D]
		self.z2D=np.r_[self.z2D]

		Ri,center = self.calibration.optimizeCircle(self.x2D,self.z2D)
		
		self.xc, self.zc = center
		
		self.R = Ri.mean()
		residu = sum((Ri - self.R)**2)

		theta_fit = np.linspace(-np.pi, np.pi, 180)

		x_fit2 = self.xc + self.R*np.cos(theta_fit)
		z_fit2 = self.zc + self.R*np.sin(theta_fit)

		
		self.clearPlot()
			
		self.circlePlot=self.ax.plot(x_fit2, z_fit2, 'k--', lw=2)
	
		self.centerPlot=self.ax.plot([self.xc], [self.zc], 'gD', mec='r', mew=1)

		# plot the residu fields
		nb_pts = 100

		# self.canvas.draw()
		xmin=(self.xc-self.R)*1.05
		xmax=(self.xc+self.R)*1.05
		ymin=(self.zc-self.R)/1.05
		ymax=(self.zc+self.R)*1.05

		vmin = min(xmin, ymin)
		vmax = max(xmax, ymax)

		xg, zg = np.ogrid[vmin-4*self.R:(vmin+4*self.R):nb_pts*1j, vmax-4*self.R:vmax+self.R:nb_pts*1j]
		xg = xg[..., np.newaxis]
		zg = zg[..., np.newaxis]

		Rig    = np.sqrt( (xg - self.x2D)**2 + (zg - self.z2D)**2 )
		Rig_m  = Rig.mean(axis=2)[..., np.newaxis]  
		residu = np.sum( (Rig-Rig_m)**2 ,axis=2)
		lvl = np.exp(np.linspace(np.log(residu.min()), np.log(residu.max()), 15))

		self.residuContour=self.ax.contourf(xg.flat, zg.flat, residu.T, lvl, alpha=0.4, cmap=cm.Purples_r) # , norm=colors.LogNorm())
		
		self.residuColors=self.ax.contour (xg.flat, zg.flat, residu.T, lvl, alpha=0.8, colors="lightblue")

		# plot the data
		self.ax.plot(self.x2D, self.z2D, 'ro', label='Pattern corner', ms=8, mec='b', mew=1)
		# self.legend=self.ax.legend(loc='best',labelspacing=0.1 )

		self.ax.grid()

		label= "Center: xc="+str(self.xc)+" zc="+str(self.zc)
		self.ax.set_title(label)

		self.on_size(0)
	
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
		
	def hide(self):
		if hasattr(self,'canvas'):
			self.canvas.Show(False)
		self.Show(False)
		# self.getPanel().Unbind(wx.EVT_SIZE)
	def show(self):
		if hasattr(self,'canvas'):
			self.canvas.Show(True)
		self.Show(True)

	def clearPlot(self):
		if hasattr(self,'circlePlot'):
			
			self.circlePlot.pop().remove()
			self.centerPlot.pop().remove()

			self.ax.grid()
			for coll in self.residuContour.collections:
				self.ax.collections.remove(coll)
			for coll in self.residuColors.collections:
				self.ax.collections.remove(coll)

	def setLayout(self):
		self.ghbox = wx.BoxSizer(wx.HORIZONTAL)
		self.ghbox.Add(self,1,wx.EXPAND,0)
		self.parent.SetSizer(self.ghbox)
		if self.scanner.isConnected:
			self.showPatternHelp()	
		else:
			self.showSocketHelp()
		self._upPanel.Layout()
		self.parent.Layout()

	def showPatternHelp(self):
		self.guideView.setImage(wx.Image(getPathForImage("patternPosition.png")))
		if hasattr(self,'text'):
			self.text.SetLabel(_("Place the pattern here and press Next"))
		else:
			self.text=wx.StaticText(self.guideView,label=_("Place the pattern here and press Next"))	
	
	def showSocketHelp(self):
		self.guideView.setImage(wx.Image(getPathForImage("socket.png")))
		if hasattr(self,'text'):
			self.text.SetLabel(_("Please connect the scanner"))
		else:
			self.text=wx.StaticText(self.guideView,label=_("Please connect the scanner"))		
		self.parent.parent.Bind(wx.EVT_TOOL , self.onConnectToolClicked,self.parent.parent.connectTool)
	
	def onConnectToolClicked(self,event):
		self.parent.parent.enableLabelTool(self.parent.parent.disconnectTool,True)
		self.parent.parent.enableLabelTool(self.parent.parent.connectTool,False)
		self.scanner.connect()
		self.showPatternHelp()
		self.getRightButton().Enable()

	def onDisconnectToolClicked(self,event):
		
		self.scanner.disconnect() # Not working camera disconnect :S
		# TODO: Check disconnection
		self.parent.parent.enableLabelTool(self.parent.parent.connectTool, True)
		self.parent.parent.enableLabelTool(self.parent.parent.disconnectTool,False)
		self.parent.parent.loadInit(0)

	def acceptCalibration(self,event):
		self.calibration.setExtrinsic(self.xc, self.zc)
		self.parent.parent.loadInit(0)

class IntrinsicsPanel(wx.lib.scrolledpanel.ScrolledPanel):

	def __init__(self,parent,calibration):

		wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, id=wx.ID_ANY)

		self.parent=parent
		self.calibration=calibration
		self.calibration.updateProfileToAllControls()
		self._vCalMatrix= [["fx=","","cx="],["","fy=","cy="],["","",""]] 
		
		self._vDistortionVector=["k1=","k2=","p1=","p2=","k3="] 
	
		self._editControl=False  # True means editing state
		self.load()
		self.SetupScrolling(scroll_x = False)

	def load(self):
		self.scaleFactor=3*40

		self._intrinsicTitle=wx.StaticText(self,label=_("Step 1: Intrinsic parameters"))
		font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL,True)
		
		self._intrinsicTitle.SetFont(font)

		vbox=wx.BoxSizer(wx.VERTICAL)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._intrinsicTitle,0,wx.ALL,20)
		hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)

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

		self.loadMatrices(self,vbox)

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
		self.Bind(wx.EVT_SIZE, self.on_size)
		
	def loadMatrices(self,parent,sizer):
		#camera matrix
		font = wx.Font(12, wx.SCRIPT, wx.NORMAL, wx.BOLD)
		self._camMatrixTitle=wx.StaticBox(parent,label=_("Camera Matrix"))
		self._camMatrixTitle.SetFont(font)
		boxSizer = wx.StaticBoxSizer(self._camMatrixTitle,wx.HORIZONTAL)
		boxSizer.Add((-1,50),0,wx.ALL,5)

		self._visualMatrix=[[0 for j in range(len(self._vCalMatrix))] for i in range(len(self._vCalMatrix[0]))]
		self._visualCtrlMatrix=[[0 for j in range(len(self._visualMatrix))] for i in range(len(self._visualMatrix[0]))]
		
		for j in range(len(self._vCalMatrix[0])):
			vbox2 = wx.BoxSizer(wx.VERTICAL)  

			for i in range (len(self._vCalMatrix)):
				label=str(self._vCalMatrix[i][j]) + str(self.calibration._calMatrix[i][j])
			
				self._visualMatrix[i][j]= wx.StaticText(parent,label=label)

				self._visualCtrlMatrix[i][j]=wx.TextCtrl(parent,-1,str(self.calibration._calMatrix[i][j]),style=wx.TE_RICH)
				vbox2.Add(self._visualMatrix[i][j],0,wx.EXPAND|wx.TOP,27)
				
				vbox2.Add(self._visualCtrlMatrix[i][j],0,wx.EXPAND|wx.TOP,15)
				self._visualCtrlMatrix[i][j].Show(False)
			
			boxSizer.Add(vbox2,1,wx.EXPAND | wx.ALL,5)

		boxSizer.Add((-1,50),0,wx.ALL,5)

		sizer.Add(boxSizer,0,wx.EXPAND|wx.ALL,30)
		
		#distortion coefficients
		self._distortionCoeffStaticText = wx.StaticBox(parent, label=_("Distortion coefficients"))
		self._distortionCoeffStaticText.SetFont(font)
		boxSizer = wx.StaticBoxSizer(self._distortionCoeffStaticText,wx.VERTICAL)

		vboxAux= wx.BoxSizer(wx.VERTICAL)
		hboxRow1=wx.BoxSizer(wx.HORIZONTAL)
		hboxRow2=wx.BoxSizer(wx.HORIZONTAL)
		self._visualDistortionVector=[0 for j in range(len(self.calibration._distortionVector))]
		self._visualCtrlDistortionVector=[0 for j in range(len(self.calibration._distortionVector))]
		for i in range(len(self._vDistortionVector)):
			
			label=str(self._vDistortionVector[i])+str(self.calibration._distortionVector[i])
			self._visualDistortionVector[i]=wx.StaticText(parent,label=label)
			self._visualCtrlDistortionVector[i]=wx.TextCtrl(parent,value=str(self.calibration._distortionVector[i]),style=wx.TE_RICH)
			self._visualCtrlDistortionVector[i].Show(False)
			if i<3:	
				hboxRow1.Add( self._visualCtrlDistortionVector[i],1,wx.ALL|wx.EXPAND,5)	
				hboxRow1.Add( self._visualDistortionVector[i],1,wx.ALL|wx.EXPAND,5)
			else:
				hboxRow2.Add( self._visualCtrlDistortionVector[i],1,wx.ALL|wx.EXPAND,5)	
				hboxRow2.Add( self._visualDistortionVector[i],1,wx.ALL|wx.EXPAND,5)
		hboxRow2.Add( (-1,-1),1,wx.ALL|wx.EXPAND,5)
		vboxAux.Add(hboxRow1,0,wx.EXPAND|wx.TOP,15)
		vboxAux.Add(hboxRow2,0,wx.EXPAND|wx.TOP,15)
		boxSizer.Add(vboxAux,-1,wx.EXPAND,0)

		sizer.Add(boxSizer,0,wx.ALIGN_LEFT|wx.ALL|wx.EXPAND,30)


	def start(self,event):
		
		self.parent.parent.loadPagePattern(0)

	def restore(self,event):
		
		self.calibration.restoreCalibrationMatrix()
		self.calibration.restoreDistortionVector()
		self.reload()


	def edit(self,event):
		
		if self._editControl:
			# means finish editing = save
			if  self.checkMatrices():
				for i in range(len(self._visualMatrix)):
					for j in range(len(self._visualMatrix[0])):
						
						self._visualCtrlMatrix[i][j].Show(False)
						self._visualMatrix[i][j].Show(True)
						
						self.calibration._calMatrix.itemset((i,j),self._visualCtrlMatrix[i][j].GetValue())
						label=str(self._vCalMatrix[i][j]) + str(self.calibration._calMatrix[i][j])
				
						self._visualMatrix[i][j].SetLabel(label)
				for i in range(len(self._vDistortionVector)):
					
					self._visualDistortionVector[i].Show(True)
					self._visualCtrlDistortionVector[i].Show(False)
					self.calibration._distortionVector.itemset((i),self._visualCtrlDistortionVector[i].GetValue())
					label=str(self._vDistortionVector[i])+str(self.calibration._distortionVector[i])
					self._visualDistortionVector[i].SetLabel(label)
				self._editControl=False
				self.calibration.saveCalibrationMatrix()
				self.calibration.saveDistortionVector()
			
		else:
			# means start editing 
			for i in range(len(self._visualMatrix)):
				for j in range(len(self._visualMatrix[0])):
					
					self._visualCtrlMatrix[i][j].Show(True)
					self._visualMatrix[i][j].Show(False)
			self._editControl=True
					
			for i in range(len(self._vDistortionVector)):
				self._visualDistortionVector[i].Show(False)
				self._visualCtrlDistortionVector[i].Show(True)
		self.reload()
				
	def checkMatrices(self):
		isCorrect=True
		for i in range(len(self._visualMatrix)):
			for j in range(len(self._visualMatrix[0])):
				
				if self.checkFloat(self._visualCtrlMatrix[i][j].GetValue()):
					self._visualCtrlMatrix[i][j].SetBackgroundColour(wx.WHITE)
				else:
					isCorrect=False
					self._visualCtrlMatrix[i][j].SetBackgroundColour(wx.RED)
				
		for i in range(len(self._vDistortionVector)):
			
			if self.checkFloat(self._visualCtrlDistortionVector[i].GetValue()):
				self._visualCtrlDistortionVector[i].SetBackgroundColour(wx.WHITE)
			else:
				isCorrect=False
				self._visualCtrlDistortionVector[i].SetBackgroundColour(wx.RED)
		return isCorrect
	def checkFloat(self,number):
		try:
			float(number)
			return True
		except ValueError:
			return False

	def save(self,event):
		print "save"
	def scale_bitmap(self,bitmap, width, height):
		image = wx.ImageFromBitmap(bitmap)
		image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
		result = wx.BitmapFromImage(image)
		return result
	def reload(self):
		x,_= self.GetClientSize()
		optimalTrimming=x/(self.scaleFactor)
		self._trimmedCalMatrix=np.around(np.copy(self.calibration._calMatrix),decimals=optimalTrimming)
		self._trimmedDistortionVector=np.around(np.copy(self.calibration._distortionVector),decimals=optimalTrimming)
		
		for i in range(len(self._visualMatrix)):
			for j in range(len(self._visualMatrix[0])):

				self._visualCtrlMatrix[i][j].SetValue(str(self.calibration._calMatrix[i][j]))
				label=str(self._vCalMatrix[i][j]) + str(self._trimmedCalMatrix[i][j])
				self._visualMatrix[i][j].SetLabel(label)

		for i in range(len(self._vDistortionVector)):
			
			self._visualCtrlDistortionVector[i].SetValue(str(self.calibration._distortionVector[i]))
			label=str(self._vDistortionVector[i])+str(self._trimmedDistortionVector[i])
			self._visualDistortionVector[i].SetLabel(label)	

		self.Layout()
	def on_size(self,event):
		
		self.reload()

class ExtrinsicsPanel(wx.lib.scrolledpanel.ScrolledPanel):

	def __init__(self,parent,calibration):
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, id=wx.ID_ANY)
		self.parent=parent
		self.calibration=calibration
		self._vRotMatrix= [["r11=","r12=","r13="],["r21=","r22=","r23="],["r31=","r32=","r33="]] 
		
		self._vTransMatrix= [["t1="],["t2="],["t3="]] # TODO connect with scanner's calibration matrix

		self._editControl=False

		self.load()
		self.SetupScrolling(scroll_x = False)

	def load(self):
		self.scaleFactor=4*40

		self._extrinsicTitle=wx.StaticText(self,label=_("Step 2: Extrinsic parameters"))
		font = wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.NORMAL,True)
		
		self._extrinsicTitle.SetFont(font)

		vbox=wx.BoxSizer(wx.VERTICAL)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._extrinsicTitle,0,wx.ALL,20)
		hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)

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

		#rotation matrix
		font = wx.Font(12, wx.SCRIPT, wx.NORMAL, wx.BOLD)
		self.transMatrixTitle=wx.StaticBox(self,label=_("Transformation Matrix"))
		self.transMatrixTitle.SetFont(font)
		boxSizer = wx.StaticBoxSizer(self.transMatrixTitle,wx.HORIZONTAL)
		boxSizer.Add((-1,50),0,wx.ALL,5)

		self._visualMatrix=[[0 for j in range(len(self._vRotMatrix)+1)] for i in range(len(self._vRotMatrix[0]))]
		self._visualCtrlMatrix=[[0 for j in range(len(self._vRotMatrix)+1)] for i in range(len(self._vRotMatrix[0]))]
		for j in range(len(self._vRotMatrix[0])):
			vbox2 = wx.BoxSizer(wx.VERTICAL)  
			for i in range (len(self._vRotMatrix)):
				label=str(self._vRotMatrix[i][j])+ str(self.calibration._rotMatrix[i][j])
				self._visualCtrlMatrix[i][j]=wx.TextCtrl(self,-1,str(self.calibration._rotMatrix[i][j]),style=wx.TE_RICH)
				
				self._visualMatrix[i][j]= wx.StaticText(self,label=label)
				vbox2.Add(self._visualMatrix[i][j],0,wx.EXPAND |wx.TOP,27)
				vbox2.Add(self._visualCtrlMatrix[i][j],0,wx.EXPAND | wx.TOP,15)

				self._visualCtrlMatrix[i][j].Show(False)
			boxSizer.Add(vbox2,1,wx.EXPAND | wx.ALL,5)

		vbox2 = wx.BoxSizer(wx.VERTICAL)
		for j in range(len(self._vTransMatrix)):
			
			label=str(self._vTransMatrix[j][0])+ str(self.calibration._transMatrix[j][0])
			self._visualCtrlMatrix[j][3]=wx.TextCtrl(self,-1,str(self.calibration._transMatrix[j][0]),style=wx.TE_RICH)
				
			self._visualMatrix[j][3]= wx.StaticText(self,label=label)
			self._visualCtrlMatrix[j][3].Show(False)
			vbox2.Add(self._visualMatrix[j][3],0,wx.EXPAND |wx.TOP,27)
			vbox2.Add(self._visualCtrlMatrix[j][3],0,wx.EXPAND | wx.TOP,15)

		boxSizer.Add(vbox2,1,wx.EXPAND | wx.ALL,5)

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

		self.Bind(wx.EVT_SIZE, self.on_size)

	def on_size(self,event):
		
		self.reload()
		
	def start(self,event):
		self.parent.parent.loadExtrinsicCalibrationPanel(0)

	def restore(self,event):

		self.calibration.restoreRotationMatrix()
		self.calibration.restoreTranslationVector()		
		self.reload()

	def edit(self,event):
		"""Method for both saving and start editting"""
		
		if self._editControl:
			if self.checkMatrices():

				for i in range(len(self._visualMatrix)):
					for j in range(len(self._visualMatrix[0])-1):
						
						self._visualCtrlMatrix[i][j].Show(False)
						self._visualMatrix[i][j].Show(True)
						self._editControl=False
						self.calibration._rotMatrix.itemset((i,j),self._visualCtrlMatrix[i][j].GetValue())
						
						label=str(self._vRotMatrix[i][j]) + str(self.calibration._rotMatrix[i][j])		
						self._visualMatrix[i][j].SetLabel(label)
				for j in range(len(self._vTransMatrix)):
					
					self._visualMatrix[j][3].Show(True)
					self._visualCtrlMatrix[j][3].Show(False)
					self.calibration._transMatrix.itemset((j),self._visualCtrlMatrix[j][3].GetValue())
					label=str(self._vTransMatrix[j][0])+str(self.calibration._transMatrix[j][0])
					self._visualMatrix[j][3].SetLabel(label)

				self.calibration.saveRotationMatrix()
				self.calibration.saveTranslationVector()
				
		else:
			for i in range(len(self._visualMatrix)):
				for j in range(len(self._visualMatrix[0])):
					
					self._visualCtrlMatrix[i][j].Show(True)
					self._visualMatrix[i][j].Show(False)
					self._editControl=True					
			
		self.reload()

	def save(self,event):
		print "save"

	def scale_bitmap(self,bitmap, width, height):
		image = wx.ImageFromBitmap(bitmap)
		image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
		result = wx.BitmapFromImage(image)
		return result

	def reload(self):
		x,_= self.GetClientSize()
		optimalTrimming=x/(self.scaleFactor)
		self._trimmedRotMatrix=np.around(np.copy(self.calibration._rotMatrix),decimals=optimalTrimming)
		self._trimmedTransMatrix=np.around(np.copy(self.calibration._transMatrix),decimals=optimalTrimming)
		for i in range(len(self._visualMatrix)):
			for j in range(len(self._visualMatrix[0])-1):

				self._visualCtrlMatrix[i][j].SetValue(str(self.calibration._rotMatrix[i][j]))
				label=str(self._vRotMatrix[i][j]) + str(self._trimmedRotMatrix[i][j])
				self._visualMatrix[i][j].SetLabel(label)

		for j in range(len(self._vTransMatrix)):
			
			self._visualCtrlMatrix[j][3].SetValue(str(self.calibration._transMatrix[j][0]))
			label=str(self._vTransMatrix[j][0])+str(self._trimmedTransMatrix[j][0])
			self._visualMatrix[j][3].SetLabel(label)

		self.Layout()

	def checkMatrices(self):
		isCorrect=True
		for i in range(len(self._visualMatrix)):
			for j in range(len(self._visualMatrix[0])):
				
				if self.checkFloat(self._visualCtrlMatrix[i][j].GetValue()):
					self._visualCtrlMatrix[i][j].SetBackgroundColour(wx.WHITE)
				else:
					isCorrect=False
					self._visualCtrlMatrix[i][j].SetBackgroundColour(wx.RED)
				
		return isCorrect

	def checkFloat(self,number):
		try:
			float(number)
			return True
		except ValueError:
			return False