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

from horus.util import resources



import random
import numpy as np

class CalibrationWorkbench(Workbench):

	def __init__(self, parent):
		Workbench.__init__(self, parent, 1, 1)

		self.load()

	def load(self):

		self.toolbar.AddLabelTool(wx.ID_EXIT, '', wx.Bitmap(resources.getPathForImage("connect.png")))
		self.toolbar.Realize()

		self._panel.parent=self
		self._intrinsicsPanel=IntrinsicsPanel(self._panel)
		self._extrinsicsPanel=ExtrinsicsPanel(self._panel)

		hbox = wx.BoxSizer(wx.HORIZONTAL)

		hbox.Add(self._intrinsicsPanel,1,wx.EXPAND|wx.ALL,40)
		hbox.Add(self._extrinsicsPanel,1,wx.EXPAND|wx.ALL,40)
		self._panel.SetSizer(hbox)
		#self.loadPagePattern()

	def loadPagePattern(self):
		self._intrinsicsPanel.Show(False)
		self._extrinsicsPanel.Show(False)
		self._patternPanel=PatternPanel(self._panel)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self._patternPanel,1,wx.EXPAND,0)
		self._panel.SetSizer(hbox)
		self.Layout()

class PatternPanel(Page):
	def __init__(self,parent):
		Page.__init__(self,parent)
		self.load()	
	def load(self):
		print "loading calibration"
class IntrinsicsPanel(wx.Panel):

	def __init__(self,parent):

		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY,style=wx.SUNKEN_BORDER)
		self.parent=parent
		self._vCalMatrix= [["fx= ","","cx= "],["","fy= ","cy= "],["","",""]] # TODO connect with scanner's calibration matrix
		self._calMatrix=np.array([[  1.39809096e+03  , 0.00000000e+00 ,  4.91502299e+02], [  0.00000000e+00 ,  1.43121118e+03  , 6.74406283e+02], [  0.00000000e+00 ,  0.00000000e+00  , 1.00000000e+00]])
		self._calMatrixDefault=np.array([[  1.39809096e+03  , 0.00000000e+00 ,  4.91502299e+02], [  0.00000000e+00 ,  1.43121118e+03  , 6.74406283e+02], [  0.00000000e+00 ,  0.00000000e+00  , 1.00000000e+00]])
		
		self._vDistortionVector=["k1=","k2=","p1=","p2=","k3="] 
		self._distortionVector= np.array([ 0.11892648 ,-0.24087801 , 0.01288427 , 0.00628766 , 0.01007653])
		self._distortionVectorDefault= np.array([ 0.11892648 ,-0.24087801 , 0.01288427 , 0.00628766 , 0.01007653])
		
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
		self.loadPagePattern()

	def restore(self,event):
		print "restore"
		for i in range(len(self._visualMatrix)):
			for j in range(len(self._visualMatrix[0])):

				self._calMatrix.itemset((i,j),self._calMatrixDefault[i][j])
				
				label=str(self._vCalMatrix[i][j]) + str(self._calMatrix[i][j])
		
				self._visualMatrix[i][j].SetLabel(label)
		for i in range(len(self._vDistortionVector)):
			
			self._distortionVector.itemset((i),self._distortionVectorDefault[i])
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

class ExtrinsicsPanel(wx.Panel):

	def __init__(self,parent):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY,style=wx.SUNKEN_BORDER)
		self._vRotMatrix= [["r11=","r12=","r13="],["r21=","r22=","r23="],["r31=","r32=","r33="]] # TODO connect with scanner's calibration matrix
		self._rotMatrix=np.array([[ 0.99970814 , 0.02222752 ,-0.00946474], [ 0.00930233 , 0.00739852 , 0.99992936],[ 0.02229597, -0.99972556 , 0.00718959]])
		self._rotMatrixDefault=np.array([[ 0.99970814 , 0.02222752 ,-0.00946474], [ 0.00930233 , 0.00739852 , 0.99992936],[ 0.02229597, -0.99972556 , 0.00718959]])
		
		self._vTransMatrix= [["t1="],["t2="],["t3="]] # TODO connect with scanner's calibration matrix
		self._transMatrix=np.array([[  -5.56044557],[  73.33950448], [ 328.54553044]])
		self._transMatrixDefault=np.array([[  -5.56044557],[  73.33950448], [ 328.54553044]])
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
		
		print self._visualMatrix
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
		print "Start"
	def restore(self,event):
		print "restore"
		for i in range(len(self._visualMatrix)):
			for j in range(len(self._visualMatrix[0])-1):

				self._rotMatrix.itemset((i,j),self._rotMatrixDefault[i][j])
				
				label=str(self._vRotMatrix[i][j]) + str(self._rotMatrix[i][j])
		
				self._visualMatrix[i][j].SetLabel(label)
		for j in range(len(self._vTransMatrix)):
			
			self._transMatrix.itemset((j),self._transMatrixDefault[j])
			label=str(self._vTransMatrix[j])+str(self._transMatrix[j])
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
