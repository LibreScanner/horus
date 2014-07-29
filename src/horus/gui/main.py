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
from horus.engine.calibration import *

from horus.util import profile, resources, meshLoader

from horus.gui.control import ControlWorkbench
from horus.gui.scanning import ScanningWorkbench
from horus.gui.calibration import CalibrationWorkbench
from horus.gui.preferences import PreferencesDialog

from horus.engine.scanner import *
from horus.util.avrHelpers import AvrDude

class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=_("Horus: 3d scanning for everyone"),
                                                size=(640+300,480+100))
        ###-- Initialize Engine

        #-- TODO: only if profile setting is None or it isn't working

        serialList = self.serialList()
        if len(serialList) > 0:
            profile.putProfileSetting('serial_name', serialList[0])
        # videoList = self.videoList()
        # if len(videoList) > 0:
        #     profile.putProfileSetting('camera_id', int(videoList[0][-1:]))
            
        self.scanner = Scanner(self)
        self.calibration = Calibration(self)

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
        #self.menuBasicMode = self.menuEdit.AppendCheckItem(wx.NewId(), _("Basic Mode"))
        #self.menuExpertMode = self.menuEdit.AppendCheckItem(wx.NewId(), _("Expert Mode"))
        #self.menuEdit.AppendSeparator()
        self.menuPreferences = self.menuEdit.Append(wx.NewId(), _("Preferences"))
        menuBar.Append(self.menuEdit, _("Edit"))

        #-- Menu View
        menuView = wx.Menu()
        self.menuWorkbenchSelector = menuView.AppendCheckItem(wx.NewId(), _("Workbench Selector"))
        self.menuWorkbench = wx.Menu()
        self.menuWorkbenchMain = self.menuWorkbench.AppendRadioItem(wx.NewId(), _("Main"))
        self.menuWorkbenchControl = self.menuWorkbench.AppendRadioItem(wx.NewId(), _("Control"))
        self.menuWorkbenchCalibration = self.menuWorkbench.AppendRadioItem(wx.NewId(), _("Calibration"))
        self.menuWorkbenchScanning = self.menuWorkbench.AppendRadioItem(wx.NewId(), _("Scanning"))
        menuView.AppendMenu(wx.NewId(), _("Workbench"), self.menuWorkbench)
        menuBar.Append(menuView, _("View"))

        #-- Menu Help
        menuHelp = wx.Menu()
        menuAbout = menuHelp.Append(wx.ID_ABOUT, _("About"))
        menuBar.Append(menuHelp, _("Help"))

        self.SetMenuBar(menuBar)

        #-- Create Combobox Workbench Selector

        self.workbenchList = {}

        self.workbenchList[_("Main")] = 'main'
        self.workbenchList[_("Control")] = 'control'
        self.workbenchList[_("Calibration")] = 'calibration'
        self.workbenchList[_("Scanning")] = 'scanning'

        keylist = [_("Main"), _("Control"), _("Calibration"), _("Scanning")]

        self.comboBoxWorkbench = wx.ComboBox(self, -1, value=keylist[0], choices=keylist, style=wx.CB_READONLY)

        ##-- Create Workbenchs

        self.mainWorkbench = MainWorkbench(self)
        self.controlWorkbench = ControlWorkbench(self)
        self.scanningWorkbench = ScanningWorkbench(self)
        self.calibrationWorkbench = CalibrationWorkbench(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.comboBoxWorkbench, 0, wx.ALL|wx.EXPAND, 6)
        sizer.Add(self.mainWorkbench, 1, wx.EXPAND)
        sizer.Add(self.controlWorkbench, 1, wx.EXPAND)
        sizer.Add(self.calibrationWorkbench, 1, wx.EXPAND)
        sizer.Add(self.scanningWorkbench, 1, wx.EXPAND)
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

        self.Bind(wx.EVT_MENU, self.onWorkbenchSelectorClicked, self.menuWorkbenchSelector)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, self.menuWorkbenchMain)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, self.menuWorkbenchControl)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, self.menuWorkbenchCalibration)
        self.Bind(wx.EVT_MENU, self.onWorkbenchSelected, self.menuWorkbenchScanning)

        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)

        self.Bind(wx.EVT_COMBOBOX, self.onComboBoxWorkbenchSelected, self.comboBoxWorkbench)

        self.updateProfileToAllControls()

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
        prefDialog.ShowModal()
        wx.CallAfter(prefDialog.Show)

    def onWorkbenchSelectorClicked(self, event):
        """ """
        if self.menuWorkbenchSelector.IsChecked():
            self.comboBoxWorkbench.Show()
            profile.putPreference('workbench_selector', True)
        else:
            self.comboBoxWorkbench.Hide()
            profile.putPreference('workbench_selector', False)
        self.Layout()

    def onWorkbenchSelected(self, event):
        """ """
        currentWorkbench = {self.menuWorkbenchMain.GetId()        : 'main',
                            self.menuWorkbenchControl.GetId()     : 'control',
                            self.menuWorkbenchCalibration.GetId() : 'calibration',
                            self.menuWorkbenchScanning.GetId()    : 'scanning'}.get(event.GetId())

        if currentWorkbench is not None:
            profile.putPreference('workbench', currentWorkbench)
        else:
            profile.putPreference('workbench', 'main')

        self.workbenchUpdate()

    def onComboBoxWorkbenchSelected(self, event):
        """ """
        currentWorkbench = self.workbenchList[self.comboBoxWorkbench.GetValue()]

        if currentWorkbench is not None:
            profile.putPreference('workbench', currentWorkbench)
        else:
            profile.putPreference('workbench', 'main')

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
        info.SetLicence("""Horus is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 3 of the License,
or (at your option) any later version.

Horus is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the GNU General Public License for more details. You should have 
received a copy of the GNU General Public License along with File Hunter; 
if not, write to the Free Software Foundation, Inc., 59 Temple Place, 
Suite 330, Boston, MA  02111-1307  USA""")
        info.AddDeveloper(u'Jesús Arroyo\n Álvaro Velad')
        info.AddDocWriter(u'Jesús Arroyo')
        info.AddArtist(u'Jesús Arroyo')
        info.AddTranslator(u'Jesús Arroyo\n Álvaro Velad')

        wx.AboutBox(info)

    def updateProfileToAllControls(self):
        """ """
        self.controlWorkbench.updateProfileToAllControls()
        self.scanningWorkbench.updateProfileToAllControls()

        if profile.getPreferenceBool('workbench_selector'):
            self.comboBoxWorkbench.Show()
            self.menuWorkbenchSelector.Check(True)
        else:
            self.comboBoxWorkbench.Hide()
            self.menuWorkbenchSelector.Check(False)

        self.workbenchUpdate()
        self.Layout()

    def updateEngine(self):
        self.scanner.initialize(profile.getProfileSettingInteger('camera_id'),
                                profile.getProfileSetting('serial_name'),
                                profile.getProfileSettingFloat('step_degrees'),
                                profile.getProfileSettingInteger('step_delay'))

        #-- TODO: add camera initialize

        self.scanner.core.initialize(profile.getProfileSetting('img_type'),
                                     profile.getProfileSettingBool('blur'),
                                     profile.getProfileSettingInteger('blur_value'),
                                     profile.getProfileSettingBool('open'),
                                     profile.getProfileSettingInteger('open_value'),
                                     np.array([profile.getProfileSettingNumpy('min_h'),
                                               profile.getProfileSettingNumpy('min_s'),
                                               profile.getProfileSettingNumpy('min_v')],np.uint8),
                                     np.array([profile.getProfileSettingNumpy('max_h'),
                                               profile.getProfileSettingNumpy('max_s'),
                                               profile.getProfileSettingNumpy('max_v')],np.uint8),
                                     profile.getProfileSettingBool('use_compact'),
                                     profile.getProfileSettingInteger('min_rho'),
                                     profile.getProfileSettingInteger('max_rho'),
                                     profile.getProfileSettingInteger('min_h'),
                                     profile.getProfileSettingInteger('max_h'),
                                     profile.getProfileSettingInteger('z_offset'),
                                     profile.getProfileSettingFloat('step_degrees'),
                                     profile.getProfileSettingInteger('camera_width'),
                                     profile.getProfileSettingInteger('camera_height'),
                                     profile.getProfileSettingFloat('laser_angle'),
                                     profile.getProfileSettingNumpy('calibration_matrix'),
                                     profile.getProfileSettingNumpy('translation_vector'))

    def updateFirmware(self):
        avr_dude = AvrDude(port=profile.getProfileSetting('serial_name'))
        stdout, stderr = avr_dude.flash(extra_flags=["-D"])
        print stdout
        print stderr

    def workbenchUpdate(self):
        """ """
        currentWorkbench = profile.getPreference('workbench')

        wb = {'main'        : self.mainWorkbench,
              'control'     : self.controlWorkbench,
              'calibration' : self.calibrationWorkbench,
              'scanning'    : self.scanningWorkbench}

        for key in wb:
            if wb[key] is not None:
                if key == currentWorkbench:
                    wb[key].Show()
                else:
                    wb[key].Hide()

        menuWb = {'main'        : self.menuWorkbenchMain,
                  'control'     : self.menuWorkbenchControl,
                  'calibration' : self.menuWorkbenchCalibration,
                  'scanning'    : self.menuWorkbenchScanning}.get(currentWorkbench)

        if menuWb is not None:
            self.menuWorkbench.Check(menuWb.GetId(), True)

        for key in self.workbenchList:
            if self.workbenchList[key] == currentWorkbench:
                self.comboBoxWorkbench.SetValue(key)
                break

        self.menuFile.Enable(self.menuLoadModel.GetId(), currentWorkbench == 'scanning')
        self.menuFile.Enable(self.menuSaveModel.GetId(), currentWorkbench == 'scanning')
        self.menuFile.Enable(self.menuClearModel.GetId(), currentWorkbench == 'scanning')

        self.Layout()

    def serialList(self):
        return self._deviceList("SERIALCOMM", ['/dev/ttyACM*', '/dev/ttyUSB*', "/dev/tty.usb*", "/dev/cu.*", "/dev/rfcomm*"])

    def videoList(self):
        return self._deviceList("VIDEO", ['/dev/video*'])

    def _deviceList(self, win_devices, linux_devices):
        baselist=[]
        if os.name=="nt":
            if win_devices=="VIDEO":
                for i in range(10):
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened() == False:
                        break
                    cap.release()
                    baselist.append(str(i))
            else:
                import _winreg
                try:
                    key=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"HARDWARE\\DEVICEMAP\\" + win_devices)
                    i=0
                    while True:
                        try:
                            values = _winreg.EnumValue(key, i)
                        except:
                            return baselist
                        if 'USBSER' in values[0]:
                            baselist.append(values[1])
                        i+=1
                except:
                    return baselist
        else:
            for device in linux_devices:
                baselist = baselist + glob.glob(device)
        return baselist

class MainWorkbench(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        titleBox = wx.BoxSizer(wx.VERTICAL)

        self._title = wx.Panel(self)
        self._panel = wx.Panel(self)
        self._leftPanel = ItemWorkbench(self._panel, _("Control"))
        self._middlePanel = ItemWorkbench(self._panel, _("Calibration"))
        self._rightPanel = ItemWorkbench(self._panel, _("Scanning"))

        #self._title.SetBackgroundColour(wx.WHITE)
        #self._panel.SetBackgroundColour(wx.BLACK)

        self.titleText = wx.StaticText(self._title, label=_("Welcome to Horus"))
        self.titleText.SetFont((wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))

        titleBox.Add(self.titleText, 0, wx.ALL^wx.BOTTOM|wx.EXPAND, 20)
        self._title.SetSizer(titleBox)

        vbox.Add(self._title, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(self._panel, 1, wx.ALL|wx.EXPAND, 2)

        hbox.Add(self._leftPanel, 1, wx.ALL|wx.EXPAND, 20)
        hbox.Add(self._middlePanel, 1, wx.ALL|wx.EXPAND, 20)
        hbox.Add(self._rightPanel, 1, wx.ALL|wx.EXPAND, 20)

        self._panel.SetSizer(hbox)
        self._panel.Layout()

        self.Bind(wx.EVT_BUTTON, self.onWorkbenchSelected, self._leftPanel.buttonGo)
        self.Bind(wx.EVT_BUTTON, self.onWorkbenchSelected, self._middlePanel.buttonGo)
        self.Bind(wx.EVT_BUTTON, self.onWorkbenchSelected, self._rightPanel.buttonGo)

        self.SetSizer(vbox)
        self.Layout()

    def onWorkbenchSelected(self, event):
        """ """
        currentWorkbench = {self._leftPanel.buttonGo.GetId()   : 'control',
                            self._middlePanel.buttonGo.GetId() : 'calibration',
                            self._rightPanel.buttonGo.GetId()  : 'scanning'}.get(event.GetId())

        if currentWorkbench is not None:
            profile.putPreference('workbench', currentWorkbench)
        else:
            profile.putPreference('workbench', 'main')

        self.GetParent().workbenchUpdate()


from horus.gui.util.videoView import *

class ItemWorkbench(wx.Panel):

    def __init__(self, parent, titleText="Workbench", description="Workbench description", buttonText="Go"):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)
        titleBox = wx.BoxSizer(wx.VERTICAL)
        contentBox = wx.BoxSizer(wx.VERTICAL)

        title = wx.Panel(self)
        content = wx.Panel(self) #, style=wx.SUNKEN_BORDER)

        #title.SetBackgroundColour(wx.GREEN)
        #content.SetBackgroundColour(wx.BLUE)

        titleText = wx.StaticText(title, label=titleText)
        titleText.SetFont((wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)))
        descText = wx.StaticText(content, label=description)
        imageView = VideoView(self)
        imageView.setImage(wx.Image(resources.getPathForImage("horus.png")))
        self.buttonGo = wx.Button(content, wx.NewId(), label=buttonText)

        titleBox.Add(titleText, 0, wx.ALL|wx.EXPAND, 10)
        title.SetSizer(titleBox)
        contentBox.Add(descText, 0, wx.ALL|wx.EXPAND, 10)
        contentBox.Add((0, 0), 1, wx.EXPAND)
        contentBox.Add(imageView, 1, wx.ALL|wx.EXPAND, 10)
        contentBox.Add(self.buttonGo, 0, wx.ALL|wx.EXPAND, 10)
        content.SetSizer(contentBox)

        vbox.Add(title, 0, wx.ALL|wx.EXPAND, 2)
        vbox.Add(content, 1, wx.ALL|wx.EXPAND, 2)

        self.SetSizer(vbox)
        self.Layout()
