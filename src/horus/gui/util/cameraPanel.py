#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: August 2014                                                     #
# Author: Carlos Crespo <carlos.crespo@bq.com>                    		#
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

__author__ = "Carlos Crespo <carlos.crespo@bq.com>"
__license__ = "GNU General Public License v3 http://www.gnu.org/licenses/gpl.html"

import wx
import wx.lib.scrolledpanel

from horus.util import profile
from horus.util import resources

class CameraPanel(wx.lib.scrolledpanel.ScrolledPanel):
	"""
	"""
	def __init__(self, parent):
		""""""
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent=parent, size=(270, 0))

		self.SetupScrolling()

		self.main = self.GetParent().GetParent().GetParent()
		self.scanner = self.main.scanner

		##-- TODO: Refactor
		
		self.brightnessId=8416 # BRIGhtness
		self.contrastId=6017 # CONTrast
		self.saturationId=5470 # SATUration
		self.exposureId=3870   # EXPOsure

		#-- Graphic elements
		cameraControlStaticText = wx.StaticText(self, wx.ID_ANY, _("Camera Control"), style=wx.ALIGN_CENTRE)
		cameraControlStaticText.SetFont((wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

		self.brightnessText = wx.StaticText(self,label=_("Brightness"))
		self.brightnessSlider = wx.Slider(self,self.brightnessId,1,0,255,size=(150,-1), style=wx.SL_LABELS)
		self.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.release,self.brightnessSlider)
		self.Bind(wx.EVT_SCROLL_THUMBTRACK,self.onbrightnessChanged,self.brightnessSlider)		

		self.contrastText = wx.StaticText(self,label=_("Contrast"))
		self.contrastSlider = wx.Slider(self,self.contrastId,1,0,255,size=(150,-1), style=wx.SL_LABELS)
		self.Bind(wx.EVT_SCROLL_THUMBTRACK,self.oncontrastChanged,self.contrastSlider)
		self.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.release,self.contrastSlider)

		self.saturationText = wx.StaticText(self,label=_("Saturation"))
		self.saturationSlider = wx.Slider(self,self.saturationId,1,0,255,size=(150,-1), style=wx.SL_LABELS)
		self.Bind(wx.EVT_SCROLL_THUMBTRACK,self.onsaturationChanged,self.saturationSlider)
		self.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.release,self.saturationSlider)

		self.exposureText = wx.StaticText(self,label=_("Exposure"))
		self.exposureSlider = wx.Slider(self,self.exposureId,60,0,200,size=(150,-1), style=wx.SL_LABELS)
		self.Bind(wx.EVT_SCROLL_THUMBTRACK,self.onexposureChanged,self.exposureSlider)
		self.Bind(wx.EVT_SCROLL_THUMBRELEASE,self.release,self.exposureSlider)

		self.framerates = [str(30),str(25),str(20),str(15),str(10),str(5)]

		self.frameRateText = wx.StaticText(self,label=_("Frame rate"), size=(70, -1), style=wx.ALIGN_CENTRE)
		self.frameRateCombo = wx.ComboBox(self, -1, size=(150, -1), choices=self.framerates, style=wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX, self.OnSelectFrame,self.frameRateCombo)

		self.resolutions = [str((1280,960)),str((960,720)),str((800,600)),str((320,240)),str((160,120))]

		self.resolutionText = wx.StaticText(self,label=_("Resolution"), size=(70, -1), style=wx.ALIGN_CENTRE)
		self.resolutionCombo = wx.ComboBox(self, -1,str((1280,960)), size=(150, -1), choices=self.resolutions, style=wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX, self.OnSelectResolution,self.resolutionCombo)

		self.restoreButton = wx.Button(self,label=_("Restore Default"),size=(200,-1))
		self.restoreButton.Bind(wx.EVT_BUTTON,self.restoreDefault)

		image1=wx.Bitmap(resources.getPathForImage("undo.png"))

		self.undoButton = wx.BitmapButton(self, id=-1, bitmap=image1, size = (image1.GetWidth()+5, image1.GetHeight()+5))
		self.undoButton.Bind(wx.EVT_BUTTON,self.undo)
		self.undoButton.Disable()

		self.workbenchText = wx.StaticText(self,-1,label="Workbench", size=(80, -1), style=wx.ALIGN_CENTRE)
		font = wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.FONTWEIGHT_BOLD,True)
		self.workbenchText.SetFont(font)

		self.workbenchesList = ['control','calibration','scanning']
		self.workbenchesCombo = wx.ComboBox(self,-1,"control",size=(150,-1),choices=self.workbenchesList,style=wx.CB_READONLY|wx.TE_RICH)
		self.Bind(wx.EVT_COMBOBOX,self.onSelectWorkbenchesCombo,self.workbenchesCombo)
		
		self.currentWorkbench='control'

		# - Layout
		vbox = wx.BoxSizer(wx.VERTICAL)

		hbox=wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(cameraControlStaticText, 0, wx.ALL, 10)
		hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.undoButton, 0, wx.ALL, 0)
		vbox.Add(hbox,0,wx.EXPAND|wx.LEFT|wx.RIGHT,0)

		vbox.Add(wx.StaticLine(self), 0, wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.workbenchText, 0, wx.ALL, 18)
		hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.workbenchesCombo, 0, wx.TOP, 10)
		vbox.Add(hbox,0,wx.EXPAND,0)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.brightnessText, 0, wx.ALL^wx.BOTTOM, 18)
		hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.brightnessSlider, 0, wx.ALL, 0)
		vbox.Add(hbox,0,wx.EXPAND,0)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.contrastText, 0, wx.ALL^wx.BOTTOM, 18)
		hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.contrastSlider, 0, wx.ALL, 0)
		vbox.Add(hbox,0,wx.EXPAND,0)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.saturationText, 0, wx.ALL^wx.BOTTOM, 18)
		hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.saturationSlider, 0, wx.ALL, 0)
		vbox.Add(hbox,0,wx.EXPAND,0)

		hbox = wx.BoxSizer(wx.HORIZONTAL)

		hbox.Add(self.exposureText, 0, wx.ALL^wx.BOTTOM, 18)
		hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)

		hbox.Add(self.exposureSlider, 0, wx.ALL, 0)
		vbox.Add(hbox,0,wx.EXPAND,0)

		hbox = wx.BoxSizer(wx.HORIZONTAL)

		hbox.Add(self.frameRateText, 0, wx.ALL, 18)
		hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.frameRateCombo, 0, wx.TOP, 10)
		vbox.Add(hbox,0,wx.EXPAND,0)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.resolutionText, 0, wx.ALL, 18)
		hbox.Add((-1,-1),1,wx.EXPAND|wx.ALL,1)
		hbox.Add(self.resolutionCombo, 0, wx.TOP, 10)
		vbox.Add(hbox,0,wx.EXPAND,0)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.restoreButton, 0, wx.ALL, 18)
		
		vbox.Add(hbox,0,wx.ALIGN_CENTRE,0)
		self.updateProfileToAllControls()
		
		self.SetSizer(vbox)
		self.Centre()

		self.storyObjects=[]
		self.storyValues=[]
		self.flagFirstMove=True # When you drag the slider, the only undoable is the first position not the ones in between

	def onSelectWorkbenchesCombo(self,event):
		value = self.workbenchesList[int(event.GetSelection())]
		self.currentWorkbench = value
		profile.putProfileSetting('workbench', value)
		self.updateProfileToAllControls()

	def onbrightnessChanged(self,event):
		self.firstMove(event,profile.getProfileSettingInteger('brightness_'+self.currentWorkbench))
		value=self.brightnessSlider.GetValue()  
		profile.putProfileSetting('brightness_'+self.currentWorkbench, value)
		self.scanner.camera.setBrightness(value)
		

	def oncontrastChanged(self,event):
		self.firstMove(event,profile.getProfileSettingInteger('contrast_'+self.currentWorkbench))
		value=self.contrastSlider.GetValue()    
		profile.putProfileSetting('contrast_'+self.currentWorkbench, value)
		self.scanner.camera.setContrast(value)

	def onsaturationChanged(self,event):
		self.firstMove(event,profile.getProfileSettingInteger('saturation_'+self.currentWorkbench))
		value=self.saturationSlider.GetValue()  
		profile.putProfileSetting('saturation_'+self.currentWorkbench, value)
		self.scanner.camera.setSaturation(value)

	def onexposureChanged(self,event):
		self.firstMove(event,profile.getProfileSettingInteger('exposure_'+self.currentWorkbench))
		value=self.exposureSlider.GetValue()    
		profile.putProfileSetting('exposure_'+self.currentWorkbench, value)
		self.scanner.camera.setExposure(value)

	def OnSelectFrame(self,event):
		value= int(self.frameRateCombo.GetValue())
		profile.putProfileSetting('framerate_'+self.currentWorkbench, value)
		if self.scanner.isConnected:
			self.GetParent().GetParent().GetParent().timer.Stop()
			self.scanner.camera.setFps(value)
			if self.main.playing and self.scanner.camera.fps > 0:
				self.GetParent().GetParent().GetParent().timer.Start(milliseconds=(1000/self.scanner.camera.fps))
		
	def OnSelectResolution(self,event):
		resolution = self.resolutionCombo.GetValue().replace('(', '').replace(')', '')
		h = int(resolution.split(',')[1])
		w = int(resolution.split(',')[0])
		profile.putProfileSetting('camera_width_' + self.currentWorkbench, w)
		profile.putProfileSetting('camera_height_' + self.currentWorkbench, h)
		self.scanner.camera.setWidth(w)
		self.scanner.camera.setHeight(h)

	def release(self,event):
		self.flagFirstMove=True
		self.undoButton.Enable()

	def firstMove(self,event,value):
		if self.flagFirstMove:
			self.storyObjects.append(event.GetEventObject())
			self.storyValues.append(value)
			self.flagFirstMove=False

	def undo(self,event):
		
		if len(self.storyObjects)==1:
			self.undoButton.Disable()
		objectToUndo=self.storyObjects.pop()
		valueToUndo=self.storyValues.pop()
		objectToUndo.SetValue(valueToUndo)
		self.updateValue(objectToUndo)
	   

	def updateValue(self,objectToUndo):
		self.flagFirstMove=False
		if (objectToUndo.GetId() == self.brightnessId):
			self.onbrightnessChanged(0)
		elif(objectToUndo.GetId() == self.contrastId):
			self.oncontrastChanged(0)
		elif(objectToUndo.GetId() == self.saturationId):
			self.onsaturationChanged(0)
		elif(objectToUndo.GetId() == self.exposureId):
			self.onexposureChanged(0)
		self.flagFirstMove=True

	def restoreDefault(self,event):
		if self.scanner.isConnected:
			profile.resetProfileSetting('brightness_'+self.currentWorkbench)
			profile.resetProfileSetting('contrast_'+self.currentWorkbench)
			profile.resetProfileSetting('saturation_'+self.currentWorkbench)
			profile.resetProfileSetting('exposure_'+self.currentWorkbench)
			profile.resetProfileSetting('framerate_'+self.currentWorkbench)
			profile.resetProfileSetting('camera_width_'+self.currentWorkbench)
			profile.resetProfileSetting('camera_height_'+self.currentWorkbench)
			self.GetParent().GetParent().GetParent().timer.Stop()
			self.updateProfileToAllControls()
			if self.main.playing and self.scanner.camera.fps > 0:
				self.GetParent().GetParent().GetParent().timer.Start(milliseconds=(1000/self.scanner.camera.fps))
			exposure=profile.getProfileSettingInteger('exposure_'+self.currentWorkbench)
			self.scanner.camera.setExposure(exposure)

	def updateProfileToAllControls(self):
		brightness=profile.getProfileSettingInteger('brightness_' + self.currentWorkbench)
		self.brightnessSlider.SetValue(brightness)
		self.scanner.camera.setBrightness(brightness)

		contrast=profile.getProfileSettingInteger('contrast_' + self.currentWorkbench)
		self.contrastSlider.SetValue(contrast)
		self.scanner.camera.setContrast(contrast)

		saturation=profile.getProfileSettingInteger('saturation_' + self.currentWorkbench)
		self.saturationSlider.SetValue(saturation)
		self.scanner.camera.setSaturation(saturation)

		exposure=profile.getProfileSettingInteger('exposure_' + self.currentWorkbench)
		self.exposureSlider.SetValue(exposure)
		self.scanner.camera.setExposure(exposure)

		framerate=profile.getProfileSettingInteger('framerate_' + self.currentWorkbench)
		self.frameRateCombo.SetValue(str(framerate))
		self.scanner.camera.setFps(framerate)

		camera_width = profile.getProfileSettingInteger('camera_width_' + self.currentWorkbench)
		camera_height = profile.getProfileSettingInteger('camera_height_' + self.currentWorkbench)
		resolution=(camera_width, camera_height)
		self.resolutionCombo.SetValue(str(resolution))
		self.scanner.camera.setWidth(camera_width)
		self.scanner.camera.setHeight(camera_height)