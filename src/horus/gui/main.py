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

import os
import wx._core

from horus.gui.control import *
from horus.gui.viewer import *

from horus.engine.scanner import *

from horus.language.en_us import *

class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=APP_TITLE_STR,
                                                size=(640+300,480+100))
        #-- Initialize GUI
        icon = wx.Icon(os.path.join(os.path.dirname(__file__),
         "../resources/horus.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.CreateStatusBar()

        menuBar = wx.MenuBar()
        menuFile = wx.Menu()
        menuOpen = menuFile.Append(wx.ID_OPEN, MENU_OPEN_STR, MENU_OPEN_STATUS_STR)
        menuSave = menuFile.Append(wx.ID_SAVE, MENU_SAVE_STR, MENU_SAVE_STATUS_STR)
        menuFile.AppendSeparator()
        menuExit = menuFile.Append(wx.ID_EXIT, MENU_EXIT_STR, MENU_EXIT_STATUS_STR)
        menuBar.Append(menuFile, MENU_FILE_STR)
        menuHelp = wx.Menu()
        menuAbout = menuHelp.Append(wx.ID_ABOUT, MENU_ABOUT_STR, MENU_ABOUT_STATUS_STR)
        menuBar.Append(menuHelp, MENU_HELP_STR)
        self.SetMenuBar(menuBar)

        scanner = Scanner(self)

        viewer = ViewNotebook(self, scanner)
        control = ControlNotebook(self, scanner, viewer)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(control, 0, wx.ALL|wx.EXPAND, 10)
        sizer.Add(viewer, 1, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(sizer)

        # Events
        self.Bind(wx.EVT_MENU, self.onOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.onSave, menuSave)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)

        self.Layout()
        self.Show()


    def onOpen(self, event):
        """ """
        pass

    def onSave(self, event):
        """ """
        pass

    def onAbout(self, event):
        """ """
        description = """Horus is an open source 3D Scanner manager..."""

        licence = """Horus is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 3 of the License, 
or (at your option) any later version.

Horus is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA"""

        info = wx.AboutDialogInfo()

        icon = os.path.join(os.path.dirname(__file__),
         "../resources/images/horus.png")
        info.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_PNG))
        info.SetName('Horus')
        info.SetVersion('0.1')
        info.SetDescription(description)
        info.SetCopyright('(C) 2014 Mundo Reader S.L.')
        info.SetWebSite('http://www.bq.com')
        info.SetLicence(licence)
        info.AddDeveloper('Jesús Arroyo')
        info.AddDocWriter('Jesús Arroyo')
        info.AddArtist('Jesús Arroyo')
        info.AddTranslator('Jesús Arroyo')

        wx.AboutBox(info)

    def onExit(self, event):
        self.Close(True)
