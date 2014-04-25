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

from horus.language.multilingual import *

class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=getString("APP_TITLE_STR"),
                                                size=(640+300,480+100))
        #-- Initialize GUI
        icon = wx.Icon(os.path.join(os.path.dirname(__file__),
         "../resources/horus.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.CreateStatusBar()

        menuBar = wx.MenuBar()
        menuFile = wx.Menu()
        menuOpen = wx.MenuItem(menuFile, wx.ID_OPEN, getString("MENU_OPEN_STR"))
        menuOpen.SetBitmap(wx.Bitmap(os.path.join(os.path.dirname(__file__),
         "../resources/images/load.png")))
        menuFile.AppendItem(menuOpen)
        menuSave = wx.MenuItem(menuFile, wx.ID_SAVE, getString("MENU_SAVE_STR"))
        menuSave.SetBitmap(wx.Bitmap(os.path.join(os.path.dirname(__file__),
         "../resources/images/save.png")))
        menuFile.AppendItem(menuSave)
        menuFile.AppendSeparator()
        menuExit = wx.MenuItem(menuFile, wx.ID_EXIT, str(u'&'+getString("MENU_EXIT_STR")+u'\tCtrl+Q'))
        menuExit.SetBitmap(wx.Bitmap(os.path.join(os.path.dirname(__file__),
         "../resources/images/exit.png")))
        menuFile.AppendItem(menuExit)        
        menuBar.Append(menuFile, getString("MENU_FILE_STR"))

        # Create radio menu
        radioMenu = wx.Menu()
        menuSpanish = radioMenu.Append(wx.NewId(), getString("MENU_SPANISH_STR"), getString("MENU_SPANISH_STR"), wx.ITEM_RADIO)
        menuEnglish = radioMenu.Append(wx.NewId(), getString("MENU_ENGLISH_STR"), getString("MENU_ENGLISH_STR"), wx.ITEM_RADIO)
        if locale == ES_ES:
            menuSpanish.Check(True)
            menuEnglish.Check(False)
        else:
            menuSpanish.Check(False)
            menuEnglish.Check(True)     
        menuBar.Append(radioMenu, getString("MENU_LANGUAGE_STR"))

        menuHelp = wx.Menu()
        menuAbout = wx.MenuItem(menuHelp, wx.ID_ABOUT, getString("MENU_ABOUT_STR"))
        menuAbout.SetBitmap(wx.Bitmap(os.path.join(os.path.dirname(__file__),
         "../resources/images/about.png")))
        menuHelp.AppendItem(menuAbout)
        menuBar.Append(menuHelp, getString("MENU_HELP_STR"))

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
        self.Bind(wx.EVT_MENU, self.onSpanish, menuSpanish)
        self.Bind(wx.EVT_MENU, self.onEnglish, menuEnglish)
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
        info = wx.AboutDialogInfo()

        icon = os.path.join(os.path.dirname(__file__),
         "../resources/images/horus.png")
        info.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_PNG))
        info.SetName(u'Horus')
        info.SetVersion(u'0.1')
        info.SetDescription(getString("HORUS_DESCRIPTION"))
        info.SetCopyright(u'(C) 2014 Mundo Reader S.L.')
        info.SetWebSite(u'http://www.bq.com')
        info.SetLicence(getString("HORUS_LICENSE"))
        info.AddDeveloper(u'Jesús Arroyo\n Álvaro Velad')
        info.AddDocWriter(u'Jesús Arroyo')
        info.AddArtist(u'Jesús Arroyo')
        info.AddTranslator(u'Jesús Arroyo\n Álvaro Velad')

        wx.AboutBox(info)

    def onExit(self, event):
        self.Close(True)

    def ShowMessageReset(self):
        wx.MessageBox(getString("MESSAGE_RESET_CONTENT_STR"), getString("MESSAGE_RESET_TITLE_STR"),
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
