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

from horus.gui.control import ControlWorkbench
from horus.gui.scanning import ScanningWorkbench
from horus.gui.calibration import CalibrationWorkbench

from horus.util import profile, resources

from horus.engine.scanner import *

class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=_("Horus: 3d scanning for everyone"),
                                                size=(640+300,480+100))
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
        menuOpenProfile = wx.MenuItem(menuFile, wx.ID_OPEN, _("Open Profile"))
        #menuOpenProfile.SetBitmap(wx.Bitmap(getPathForImage("load.png")))
        menuFile.AppendItem(menuOpenProfile)
        menuSaveProfile = wx.MenuItem(menuFile, wx.ID_SAVE, _("Save Profile"))
        #menuSaveProfile.SetBitmap(wx.Bitmap(getPathForImage("save.png")))
        menuFile.AppendItem(menuSaveProfile)
        menuResetProfile = wx.MenuItem(menuFile, -1 , _("Reset Profile"))
        #menuResetProfile.SetBitmap(wx.Bitmap(getPathForImage("reset.png")))
        menuFile.AppendItem(menuResetProfile)
        menuFile.AppendSeparator()
        menuExit = wx.MenuItem(menuFile, wx.ID_EXIT, _("Exit"))
        #menuExit.SetBitmap(wx.Bitmap(getPathForImage("exit.png")))
        menuFile.AppendItem(menuExit)
        menuBar.Append(menuFile, _("File"))

        #-- Menu Edit
        menuEdit = wx.Menu()
        menuEdit.AppendCheckItem(wx.ID_ANY, _("Basic Mode"))
        menuEdit.AppendCheckItem(wx.ID_ANY, _("Expert Mode"))
        menuEdit.AppendSeparator()
        menuEdit.Append(wx.ID_ANY, _("Preferences"))
        menuBar.Append(menuEdit, _("Edit"))

        #-- Menu View
        menuView = wx.Menu()
        menuWorkbench = wx.Menu()
        menuWorkbench.Append(wx.ID_ANY, _("<none>"))
        menuWorkbench.Append(wx.ID_ANY, _("Main"))
        menuWorkbench.Append(wx.ID_ANY, _("Control"))
        menuWorkbench.Append(wx.ID_ANY, _("Calibration"))
        menuWorkbench.Append(wx.ID_ANY, _("Scanning"))
        menuView.AppendMenu(wx.ID_ANY, _("Workbench"), menuWorkbench)
        menuBar.Append(menuView, _("View"))

        #-- Menu Help
        menuHelp = wx.Menu()
        menuAbout = wx.MenuItem(menuHelp, wx.ID_ABOUT, _("About"))
        #menuAbout.SetBitmap(wx.Bitmap(getPathForImage("about.png")))
        menuHelp.AppendItem(menuAbout)
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

        controlWorkbench = ControlWorkbench(self)
        scanningWorkbench = ScanningWorkbench(self)
        calibrationWorkbench = CalibrationWorkbench(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(controlWorkbench, 1, wx.EXPAND)
        sizer.Add(scanningWorkbench, 1, wx.EXPAND)
        sizer.Add(calibrationWorkbench, 1, wx.EXPAND)
        self.SetSizer(sizer)

        #controlWorkbench.Show()
        #scanningWorkbench.Show()
        #calibrationWorkbench.Show()


        ##-- Events
        self.Bind(wx.EVT_MENU, self.onOpenProfile, menuOpenProfile)
        self.Bind(wx.EVT_MENU, self.onSaveProfile, menuSaveProfile)
        self.Bind(wx.EVT_MENU, self.onResetProfile, menuResetProfile)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
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

    def updateProfileToAllControls(self):
        """ """
        #self.control.updateProfileToAllControls()
        ## TODO

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

    def onExit(self, event):
        self.Close(True)
