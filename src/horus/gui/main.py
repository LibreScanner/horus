#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------#
#                                                                       #
# This file is part of the Horus Project                                #
#                                                                       #
# Copyright (C) 2014 Mundo Reader S.L.                                  #
#                                                                       #
# Date: March 2014                                                      #
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

from horus.gui.control import *
from horus.gui.viewer import *

from horus.engine.scanner import *

from horus.util.resources import *

class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=_("Horus: 3d scanning for everyone"),
                                                size=(640+300,480+100))
        #-- Initialize GUI
        icon = wx.Icon(getPathForImage("horus.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.CreateStatusBar()

        menuBar = wx.MenuBar()
        menuFile = wx.Menu()
        menuOpenProfile = wx.MenuItem(menuFile, wx.ID_OPEN, _("Open Profile"))
        menuOpenProfile.SetBitmap(wx.Bitmap(getPathForImage("load.png")))
        menuFile.AppendItem(menuOpenProfile)
        menuSaveProfile = wx.MenuItem(menuFile, wx.ID_SAVE, _("Save Profile"))
        menuSaveProfile.SetBitmap(wx.Bitmap(getPathForImage("save.png")))
        menuFile.AppendItem(menuSaveProfile)
        menuResetProfile = wx.MenuItem(menuFile, -1 , _("Reset Profile"))
        #menuResetProfile.SetBitmap(wx.Bitmap(getPathForImage("reset.png")))
        menuFile.AppendItem(menuResetProfile)
        menuFile.AppendSeparator()
        menuExit = wx.MenuItem(menuFile, wx.ID_EXIT, str(u'&'+_("Exit")+u'\tCtrl+Q'))
        menuExit.SetBitmap(wx.Bitmap(getPathForImage("exit.png")))
        menuFile.AppendItem(menuExit)        
        menuBar.Append(menuFile, _("File"))

        """# Create radio menu
        radioMenu = wx.Menu()
        menuSpanish = radioMenu.Append(wx.NewId(), getString("MENU_SPANISH_STR"), getString("MENU_SPANISH_STR"), wx.ITEM_RADIO)
        menuEnglish = radioMenu.Append(wx.NewId(), getString("MENU_ENGLISH_STR"), getString("MENU_ENGLISH_STR"), wx.ITEM_RADIO)
        if locale == ES_ES:
            menuSpanish.Check(True)
            menuEnglish.Check(False)
        else:
            menuSpanish.Check(False)
            menuEnglish.Check(True)     
        menuBar.Append(radioMenu, getString("MENU_LANGUAGE_STR"))"""

        """# Create radio menu
        viewMenu = wx.Menu()
        self.menuVideo = viewMenu.Append(wx.NewId(), getString("MENU_VIDEO_STR"), getString("MENU_VIDEO_STR"), wx.ITEM_CHECK)
        self.menuPointCloud = viewMenu.Append(wx.NewId(), getString("MENU_POINTCLOUD_STR"), getString("MENU_POINTCLOUD_STR"), wx.ITEM_CHECK)
        f = open(os.path.join(os.path.dirname(__file__), "../resources/preferences.txt"), 'r')
        for line in f:
            if line.startswith('video'):
                if line.split('=')[1].startswith('True'):
                    self.menuVideo.Check(True)
                else:
                    self.menuVideo.Check(False)
            elif line.startswith('pointcloud'):
                if line.split('=')[1].startswith('True'):
                    self.menuPointCloud.Check(True)
                else:
                    self.menuPointCloud.Check(False)                
        f.close()
        menuBar.Append(viewMenu, getString("MENU_VIEW_STR"))"""

        menuHelp = wx.Menu()
        menuAbout = wx.MenuItem(menuHelp, wx.ID_ABOUT, _("About"))
        menuAbout.SetBitmap(wx.Bitmap(getPathForImage("about.png")))
        menuHelp.AppendItem(menuAbout)
        menuBar.Append(menuHelp, _("Help"))

        self.SetMenuBar(menuBar)

        self.scanner = Scanner(self)

        self.viewer = ViewNotebook(self, self.scanner)
        self.control = ControlNotebook(self, self.scanner, self.viewer)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.control, 0, wx.ALL|wx.EXPAND, 10)
        sizer.Add(self.viewer, 1, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(sizer)

        # Eventsº
        self.Bind(wx.EVT_MENU, self.onOpenProfile, menuOpenProfile)
        self.Bind(wx.EVT_MENU, self.onSaveProfile, menuSaveProfile)
        self.Bind(wx.EVT_MENU, self.onResetProfile, menuResetProfile)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
        #self.Bind(wx.EVT_MENU, self.onSpanish, menuSpanish)
        #self.Bind(wx.EVT_MENU, self.onEnglish, menuEnglish)
        #self.Bind(wx.EVT_MENU, self.toggleVideo, self.menuVideo)
        #elf.Bind(wx.EVT_MENU, self.togglePointCloud, self.menuPointCloud)
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
        self.control.updateProfileToAllControls()
        ## TODO

    def onAbout(self, event):
        """ """
        info = wx.AboutDialogInfo()
        icon = wx.Icon(getPathForImage("horus.ico"), wx.BITMAP_TYPE_ICO)
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

    def ShowMessageReset(self):
        wx.MessageBox(_("You must restart the application for the changes to be made"), _("Information"),
            wx.OK | wx.ICON_INFORMATION)

    def onSpanish(self, event):
        self.ShowMessageReset()
        f=open(os.path.join(os.path.dirname(__file__), "../resources/language.txt"),"w")
        f.write(ES_ES)
        f.close()

    def onEnglish(self, event):
        self.ShowMessageReset()
        f=open(os.path.join(os.path.dirname(__file__), "../resources/language.txt"),"w")
        f.write(EN_US)
        f.close() 

    def toggleVideo(self, event):        
        self.ShowMessageReset()
        s=open(os.path.join(os.path.dirname(__file__), "../resources/preferences.txt")).read()
        if self.menuVideo.IsChecked():
            s = s.replace('video=False', 'video=True')
        else:
            s = s.replace('video=True', 'video=False')           
        f = open(os.path.join(os.path.dirname(__file__), "../resources/preferences.txt"), 'w')
        f.write(s)
        f.close()

    def togglePointCloud(self, event):        
        self.ShowMessageReset()
        s=open(os.path.join(os.path.dirname(__file__), "../resources/preferences.txt")).read()
        if self.menuVideo.IsChecked():
            s = s.replace('pointcloud=False', 'pointcloud=True')
        else:
            s = s.replace('pointcloud=True', 'pointcloud=False')           
        f = open(os.path.join(os.path.dirname(__file__), "../resources/preferences.txt"), 'w')
        f.write(s)
        f.close()
