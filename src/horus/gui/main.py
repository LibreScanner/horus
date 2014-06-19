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

from horus.engine.camera import *
from horus.engine.device import *

from horus.gui.control import ControlWorkbench
from horus.gui.scanning import ScanningWorkbench
from horus.gui.calibration import CalibrationWorkbench

from horus.util import profile, resources

from horus.engine.scanner import *

class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=_("Horus: 3d scanning for everyone"),
                                                size=(640+300,480+100))

        self.wbDictionary = {'none':100, 'main':101, 'control':102, 'calibration':103, 'scanning':104}

        ###-- Initialize Engine

        self.camera = Camera()
        self.device = Device(profile.getProfileSetting('serial_name'),
                             profile.getProfileSetting('step_degrees'),
                             profile.getProfileSetting('step_delay'))

        ###-- Initialize GUI

        ##-- Set Icon
        icon = wx.Icon(resources.getPathForImage("horus.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        ##-- Status Bar
        self.CreateStatusBar()

        ##-- Menu Bar
        menuBar = wx.MenuBar()

        #--  Menu File        
        menuFile = wx.Menu()
        menuOpenProfile = menuFile.Append(wx.ID_OPEN, _("Open Profile"), _("Opens Profile .ini"))
        menuSaveProfile = menuFile.Append(wx.ID_SAVE, _("Save Profile"))
        menuResetProfile = menuFile.Append(wx.ID_RESET, _("Reset Profile"))
        menuFile.AppendSeparator()
        menuExit = menuFile.Append(wx.ID_EXIT, _("Exit"))
        menuBar.Append(menuFile, _("File"))

        #-- Menu Edit
        menuEdit = wx.Menu()
        menuBasicMode = menuEdit.AppendCheckItem(wx.ID_ANY, _("Basic Mode"))
        menuExpertMode = menuEdit.AppendCheckItem(wx.ID_ANY, _("Expert Mode"))
        menuEdit.AppendSeparator()
        menuPreferences = menuEdit.Append(wx.ID_ANY, _("Preferences"))
        menuBar.Append(menuEdit, _("Edit"))

        #-- Menu View
        menuView = wx.Menu()
        menuWorkbench = wx.Menu()
        menuWorkbenchNone = menuWorkbench.Append(self.wbDictionary['none'], _("<none>"))
        menuWorkbenchMain = menuWorkbench.Append(self.wbDictionary['main'], _("Main"))
        menuWorkbenchControl = menuWorkbench.Append(self.wbDictionary['control'], _("Control"))
        menuWorkbenchCalibration = menuWorkbench.Append(self.wbDictionary['calibration'], _("Calibration"))
        menuWorkbenchScanning = menuWorkbench.Append(self.wbDictionary['scanning'], _("Scanning"))
        menuView.AppendMenu(wx.ID_ANY, _("Workbench"), menuWorkbench)
        menuBar.Append(menuView, _("View"))

        #-- Menu Help
        menuHelp = wx.Menu()
        menuAbout = menuHelp.Append(wx.ID_ABOUT, _("About"))
        menuBar.Append(menuHelp, _("Help"))

        self.SetMenuBar(menuBar)

        ##-- Load Scanner Engine
        #self.scanner = Scanner(self)

        #self.viewer = ViewNotebook(self, self.scanner)
        #self.control = ControlNotebook(self, self.scanner, self.viewer)
        #sizer = wx.BoxSizer(wx.HORIZONTAL)
        #sizer.Add(self.control, 0, wx.ALL|wx.EXPAND, 10)
        #sizer.Add(self.viewer, 1, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 10)
        #self.SetSizer(sizer)

        ##-- Create Workbenchs

        self.controlWorkbench = ControlWorkbench(self)
        self.scanningWorkbench = ScanningWorkbench(self)
        self.calibrationWorkbench = CalibrationWorkbench(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.controlWorkbench, 1, wx.EXPAND)
        sizer.Add(self.scanningWorkbench, 1, wx.EXPAND)
        sizer.Add(self.calibrationWorkbench, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.workbenchUpdate()

        ##-- Events
        self.Bind(wx.EVT_MENU, self.onOpenProfile, menuOpenProfile)
        self.Bind(wx.EVT_MENU, self.onSaveProfile, menuSaveProfile)
        self.Bind(wx.EVT_MENU, self.onResetProfile, menuResetProfile)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)

        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, menuWorkbenchNone)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, menuWorkbenchMain)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, menuWorkbenchControl)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, menuWorkbenchCalibration)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, menuWorkbenchScanning)

        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)

        self.Layout()
        self.Show()


    def onOpenProfile(self, event):
        """ """
        dlg=wx.FileDialog(self, _("Select profile file to load"), "", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
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

    def onWorkbenchSelected(self, event):
        """ """
        currentWorkbench = {self.wbDictionary['control']     : 'control',
                            self.wbDictionary['calibration'] : 'calibration',
                            self.wbDictionary['scanning']    : 'scanning'}.get(event.GetId())

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

        self.Layout()
