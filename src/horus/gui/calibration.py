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

from horus.util import resources

import random

class CalibrationWorkbench(Workbench):

	def __init__(self, parent):
		Workbench.__init__(self, parent)

		self.load()

	def load(self):

		self._toolbar.AddLabelTool(wx.ID_EXIT, '', wx.Bitmap(resources.getPathForImage("load.png")))
		self._toolbar.Realize()


		self._intrinsicsPanel=IntrinsicsPanel(self._panel)
		self._extrinsicsPanel=ExtrinsicsPanel(self._panel)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._intrinsicsPanel,1,wx.EXPAND,0)
		hbox.Add(self._extrinsicsPanel,1,wx.EXPAND,0)
		self._panel.SetSizer(hbox)
		

class IntrinsicsPanel(wx.Panel):

	def __init__(self,parent):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

		self._matrix= [["fx",0,"cx"],[0,"fy","cy"],[0,0,1]] # TODO connect with scanner's calibration matrix
		self._distortionVector=["k1","k2","p1","p2","k3"] 
		self.rotmatrix= [["r11","r12","r13"],["r21","r22","r23"],["r31","r32","r33"]] # TODO connect with scanner's calibration matrix
		self.transmatrix= [["t1"],["t2"],["t3"]] # TODO connect with scanner's calibration matrix

		self.load()

	def load(self):

		self.SetBackgroundColour((random.randrange(255),random.randrange(255),random.randrange(255)))

		self._intrinsicTitle=wx.StaticText(self,label=_("Intrinsic parameters"))
		font = wx.Font(18, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,True)
		
		self._intrinsicTitle.SetFont(font)

		vbox=wx.BoxSizer(wx.VERTICAL)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._intrinsicTitle,0,0,0)
		vbox.Add(hbox,-1,wx.ALIGN_CENTER,0)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		font = wx.Font(12, wx.SCRIPT, wx.NORMAL, wx.BOLD)
		self._camMatrixTitle=wx.StaticText(self,label=_("Camera Matrix"))
		self._camMatrixTitle.SetFont(font)
		hbox.Add(self._camMatrixTitle,0,wx.ALL,20)
		vbox.Add(hbox,-1,wx.ALIGN_CENTER,0)

		self._visualMatrix=[[0 for j in range(len(self._matrix))] for i in range(len(self._matrix[0]))]
		for i in range(len(self._matrix)):
			hbox = wx.BoxSizer(wx.HORIZONTAL)  
			for j in range (len(self._matrix[i])):
				self._visualMatrix[i][j]= wx.StaticText(self,label=str(self._matrix[i][j]))
				hbox.Add(self._visualMatrix[i][j],0,wx.ALL,20)
			vbox.Add(hbox,-1,wx.ALIGN_CENTER,10)


		self._distortionCoeffStaticText = wx.StaticText(self, label=_("Distortion coefficients"))

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._distortionCoeffStaticText,0,wx.ALL,20)
		vbox.Add(hbox,-1,wx.ALIGN_CENTER,0)

		hbox= wx.BoxSizer(wx.HORIZONTAL)
		self._visualDistortionVector=[0 for j in range(len(self._distortionVector))]
		for i in range(len(self._distortionVector)):
			self._visualDistortionVector[i]=wx.StaticText(self,label=str(self._distortionVector[i]))
			hbox.Add( self._visualDistortionVector[i],0,wx.ALL,10)
		vbox.Add(hbox,-1,wx.ALIGN_CENTER,0)

		

		self._startButton = wx.Button(self,label=_("Start"),size=(100,-1))
		self._startButton.Bind(wx.EVT_BUTTON,self.start)

		self._restoreButton = wx.Button(self,label=_("Restore"),size=(100,-1))
		self._restoreButton.Bind(wx.EVT_BUTTON,self.restore)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._startButton,0,wx.ALL,20)
		hbox.Add(self._restoreButton,0,wx.ALL,20)
		vbox.Add(hbox,-1,wx.ALIGN_CENTER,0)

		self._editButton = wx.Button(self,label=_("Edit"),size=(100,-1))
		self._editButton.Bind(wx.EVT_BUTTON,self.edit)

		self._saveButton = wx.Button(self,label=_("Save"),size=(100,-1))
		self._saveButton.Bind(wx.EVT_BUTTON,self.save)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._editButton,0,wx.ALL,20)
		hbox.Add(self._saveButton,0,wx.ALL,20)
		vbox.Add(hbox,-1,wx.ALIGN_CENTER,0)

		self.SetSizer(vbox)
		
	def start(self,event):
		print "Start"
	def restore(self,event):
		print "restore"
	def edit(self,event):
		print "edit"
	def save(self,event):
		print "save"

class ExtrinsicsPanel(wx.Panel):

	def __init__(self,parent):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
		self.load()
	def load(self):
		self.SetBackgroundColour((random.randrange(255),random.randrange(255),random.randrange(255)))

		self._extrinsicTitle=wx.StaticText(self,label=_("Extrinsic parameters"))
		font = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
		self._extrinsicTitle.SetFont(font)

		vbox=wx.BoxSizer(wx.VERTICAL)
		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._extrinsicTitle,0,0,0)
		vbox.Add(hbox,-1,wx.ALIGN_CENTER,0)

		self._startButton = wx.Button(self,label=_("Start"),size=(100,-1))
		self._startButton.Bind(wx.EVT_BUTTON,self.start)

		self._restoreButton = wx.Button(self,label=_("Restore"),size=(100,-1))
		self._restoreButton.Bind(wx.EVT_BUTTON,self.restore)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._startButton,0,wx.ALL,20)
		hbox.Add(self._restoreButton,0,wx.ALL,20)
		vbox.Add(hbox,-1,wx.ALIGN_CENTER,0)

		self._editButton = wx.Button(self,label=_("Edit"),size=(100,-1))
		self._editButton.Bind(wx.EVT_BUTTON,self.edit)

		self._saveButton = wx.Button(self,label=_("Save"),size=(100,-1))
		self._saveButton.Bind(wx.EVT_BUTTON,self.save)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._editButton,0,wx.ALL,20)
		hbox.Add(self._saveButton,0,wx.ALL,20)

		vbox.Add(hbox,-1,wx.ALIGN_CENTER,0)

		self.SetSizer(vbox)

	def start(self,event):
		print "Start"
	def restore(self,event):
		print "restore"
	def edit(self,event):
		print "edit"
	def save(self,event):
		print "save"