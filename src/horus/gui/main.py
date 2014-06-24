#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: March & June 2014                                               #
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

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v3 http://www.gnu.org/licenses/gpl.html"

import wx._core

import os

from horus.engine.scanner import *

from horus.util import profile, resources, meshLoader

from horus.gui.preferences import PreferencesDialog
from horus.gui.control import ControlWorkbench
from horus.gui.scanning import ScanningWorkbench
from horus.gui.calibration import CalibrationWorkbench

from horus.engine.scanner import *

class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=_("Horus: 3d scanning for everyone"),
                                                size=(640+300,480+100))
        ###-- Initialize Engine

        #self.scanner = Scanner(self)
        self.scanner = Scanner(self)

        self.updateEngine()

        ###-- Initialize GUI

        ##-- Set Icon
        icon = wx.Icon(resources.getPathForImage("horus.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        ##-- Status Bar
        #self.CreateStatusBar()

        ##-- Menu Bar
        menuBar = wx.MenuBar()

        #--  Menu File        
        self.menuFile = wx.Menu()
        self.menuLoadModel = self.menuFile.Append(wx.NewId(), _("Load Model"))
        self.menuSaveModel = self.menuFile.Append(wx.NewId(), _("Save Model"))
        self.menuClearModel = self.menuFile.Append(wx.NewId(), _("Clear Model"))
        self.menuFile.AppendSeparator()
        menuOpenProfile = self.menuFile.Append(wx.NewId(), _("Open Profile"), _("Opens Profile .ini"))
        menuSaveProfile = self.menuFile.Append(wx.NewId(), _("Save Profile"))
        menuResetProfile = self.menuFile.Append(wx.NewId(), _("Reset Profile"))
        self.menuFile.AppendSeparator()
        menuExit = self.menuFile.Append(wx.ID_EXIT, _("Exit"))
        menuBar.Append(self.menuFile, _("File"))

        #-- Menu Edit
        self.menuEdit = wx.Menu()
        self.menuBasicMode = self.menuEdit.AppendCheckItem(wx.NewId(), _("Basic Mode"))
        self.menuExpertMode = self.menuEdit.AppendCheckItem(wx.NewId(), _("Expert Mode"))
        self.menuEdit.AppendSeparator()
        self.menuPreferences = self.menuEdit.Append(wx.NewId(), _("Preferences"))
        menuBar.Append(self.menuEdit, _("Edit"))

        #-- Menu View
        menuView = wx.Menu()
        menuWorkbench = wx.Menu()
        menuWorkbenchNone = menuWorkbench.Append(wx.NewId(), _("<none>"))
        #menuWorkbenchMain = menuWorkbench.Append(wx.NewId(), _("Main"))
        self.menuWorkbenchControl = menuWorkbench.Append(wx.NewId(), _("Control"))
        self.menuWorkbenchCalibration = menuWorkbench.Append(wx.NewId(), _("Calibration"))
        self.menuWorkbenchScanning = menuWorkbench.Append(wx.NewId(), _("Scanning"))
        menuView.AppendMenu(wx.NewId(), _("Workbench"), menuWorkbench)
        menuBar.Append(menuView, _("View"))

        #-- Menu Help
        menuHelp = wx.Menu()
        menuAbout = menuHelp.Append(wx.ID_ABOUT, _("About"))
        menuBar.Append(menuHelp, _("Help"))

        self.SetMenuBar(menuBar)

        ##-- Create Workbenchs

        self.controlWorkbench = ControlWorkbench(self)
        self.scanningWorkbench = ScanningWorkbench(self)
        self.calibrationWorkbench = CalibrationWorkbench(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.controlWorkbench, 1, wx.EXPAND)
        sizer.Add(self.scanningWorkbench, 1, wx.EXPAND)
        sizer.Add(self.calibrationWorkbench, 1, wx.EXPAND)
        self.SetSizer(sizer)

        ##-- Events
        self.Bind(wx.EVT_MENU, self.onLoadModel, self.menuLoadModel)
        self.Bind(wx.EVT_MENU, self.onSaveModel, self.menuSaveModel)
        self.Bind(wx.EVT_MENU, self.onClearModel, self.menuClearModel)
        self.Bind(wx.EVT_MENU, self.onOpenProfile, menuOpenProfile)
        self.Bind(wx.EVT_MENU, self.onSaveProfile, menuSaveProfile)
        self.Bind(wx.EVT_MENU, self.onResetProfile, menuResetProfile)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)

        self.Bind(wx.EVT_MENU, self.onPreferences, self.menuPreferences)

        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, menuWorkbenchNone)
        #self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, menuWorkbenchMain)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, self.menuWorkbenchControl)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, self.menuWorkbenchCalibration)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, self.menuWorkbenchScanning)

        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)

        self.workbenchUpdate()

        self.Show()

    def onLoadModel(self, event):
        dlg=wx.FileDialog(self, _("Open 3D model"), os.path.split(profile.getPreference('lastFile'))[0], style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        wildcardFilter = "All (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        wildcardFilter += "|Mesh files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())

        dlg.SetWildcard(wildcardFilter)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        filename = dlg.GetPath()
        dlg.Destroy()
        if filename is not None:
            profile.putPreference('lastFile', filename)
            self.scanningWorkbench.sceneView.loadFile(filename)

    def onSaveModel(self, event):
        if self.scanningWorkbench.sceneView._object is None:
            return

        dlg=wx.FileDialog(self, _("Save 3D model"), os.path.split(profile.getPreference('lastFile'))[0], style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        fileExtensions = meshLoader.saveSupportedExtensions()
        wildcardList = ';'.join(map(lambda s: '*' + s, fileExtensions))
        wildcardFilter = "Mesh files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        dlg.SetWildcard(wildcardFilter)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        filename = dlg.GetPath()
        dlg.Destroy()

        meshLoader.saveMesh(filename, self.scanningWorkbench.sceneView._object)

    def onClearModel(self, event):
        self.scanningWorkbench.sceneView._clearScene()

    def onOpenProfile(self, event):
        """ """
        dlg=wx.FileDialog(self, _("Select profile file to load"), "", style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        dlg.SetWildcard("ini files (*.ini)|*.ini")
        if dlg.ShowModal() == wx.ID_OK:
            profileFile = dlg.GetPath()
            profile.loadProfile(profileFile)
            self.updateProfileToAllControls()
        dlg.Destroy()

    def onSaveProfile(self, event):
        """ """
        import platform

        dlg=wx.FileDialog(self, _("Select profile file to save"), "", style=wx.FD_SAVE)
        dlg.SetWildcard("ini files (*.ini)|*.ini")
        if dlg.ShowModal() == wx.ID_OK:
            profileFile = dlg.GetPath()
            if platform.system() == 'Linux': #hack for linux, as for some reason the .ini is not appended.
                profileFile += '.ini'
            profile.saveProfile(profileFile)
        dlg.Destroy()

    def onResetProfile(self, event):
        """ """
        dlg = wx.MessageDialog(self, _("This will reset all profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Profile reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.resetProfile()
            self.updateProfileToAllControls()

    def onExit(self, event):
        self.Close(True)

    def onPreferences(self, event):
        prefDialog = PreferencesDialog(self)
        prefDialog.Centre()
        prefDialog.Show()
        prefDialog.Raise()
        wx.CallAfter(prefDialog.Show)

    def onWorkbenchSelected(self, event):
        """ """
        currentWorkbench = {self.menuWorkbenchControl.GetId()     : 'control',
                            self.menuWorkbenchCalibration.GetId() : 'calibration',
                            self.menuWorkbenchScanning.GetId()    : 'scanning'}.get(event.GetId())

        if currentWorkbench is not None:
            profile.putPreference('workbench', currentWorkbench)
        else:
            profile.putPreference('workbench', 'none')

        self.workbenchUpdate()

    def onAbout(self, event):
        """ """
        info = wx.AboutDialogInfo()
        icon = wx.Icon(resources.getPathForImage("horus.ico"), wx.BITMAP_TYPE_ICO)
        info.SetIcon(icon)
        info.SetName(u'Horus')
        info.SetVersion(u'0.1')
        info.SetDescription(_('Horus is an open source 3D Scanner manager...'))
        info.SetCopyright(u'(C) 2014 Mundo Reader S.L.')
        info.SetWebSite(u'http://www.bq.com')
        info.SetLicence(_("""Horus is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 3 of the License,
or (at your option) any later version.

Horus is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA"""))
        info.AddDeveloper(u'Jesús Arroyo\n Álvaro Velad')
        info.AddDocWriter(u'Jesús Arroyo')
        info.AddArtist(u'Jesús Arroyo')
        info.AddTranslator(u'Jesús Arroyo\n Álvaro Velad')

        wx.AboutBox(info)

    def updateProfileToAllControls(self):
        """ """
        #self.control.updateProfileToAllControls()
        self.workbenchUpdate()

    def updateEngine(self):
        self.scanner.initialize(profile.getProfileSettingInteger('camera_id'),
                               profile.getProfileSetting('serial_name'),
                               profile.getProfileSettingFloat('step_degrees'),
                               profile.getProfileSettingInteger('step_delay'))

    def workbenchUpdate(self):
        """ """
        currentWorkbench = profile.getPreference('workbench')

        self.controlWorkbench.Hide()
        self.calibrationWorkbench.Hide()
        self.scanningWorkbench.Hide()

        wb = {'control'     : self.controlWorkbench,
              'calibration' : self.calibrationWorkbench,
              'scanning'    : self.scanningWorkbench}.get(currentWorkbench)

        if wb is not None:
            wb.Show()

        self.menuFile.Enable(self.menuLoadModel.GetId(), currentWorkbench == 'scanning')
        self.menuFile.Enable(self.menuSaveModel.GetId(), currentWorkbench == 'scanning')
        self.menuFile.Enable(self.menuClearModel.GetId(), currentWorkbench == 'scanning')

        self.Layout()
