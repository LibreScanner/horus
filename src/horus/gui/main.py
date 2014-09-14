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
import time

from horus.util import profile, resources, meshLoader
from horus.util.avrHelpers import AvrDude

from horus.gui.control.main import ControlWorkbench
from horus.gui.settings.main import SettingsWorkbench
from horus.gui.scanning.main import ScanningWorkbench
from horus.gui.calibration.main import CalibrationWorkbench
from horus.gui.preferences import PreferencesDialog

from horus.engine.scanner import *
from horus.engine.calibration import *

class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=_("Horus 0.0.2"),
                                                size=(640+300,480+130))

        self.SetMinSize((600, 450))

        ###-- Initialize Engine

        #-- Serial Name initialization
        serialList = self.serialList()
        currentSerial = profile.getProfileSetting('serial_name')
        if len(serialList) > 0:
            if currentSerial not in serialList:
                profile.putProfileSetting('serial_name', serialList[0])

        #-- Video Id initialization
        videoList = self.videoList()
        currentVideoId = profile.getProfileSetting('camera_id')
        if len(videoList) > 0:
            if currentVideoId not in videoList:
                profile.putProfileSetting('camera_id', videoList[0])

        self.workbenchList = {'control'     : _("Control workbench"),
                              'settings'    : _("Settings workbench"),
                              'calibration' : _("Calibration workbench"),
                              'scanning'    : _("Scanning workbench")}
            
        self.scanner = Scanner.Instance()
        self.calibration = Calibration.Instance()

        self.updateEngineProfile()

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
        self.menuControl = wx.Menu()
        self.menuControlPanel = self.menuControl.AppendCheckItem(wx.NewId(), _("Panel"))
        self.menuControlVideo = self.menuControl.AppendCheckItem(wx.NewId(), _("Video"))
        menuView.AppendMenu(wx.NewId(), _("Control"), self.menuControl)
        self.menuSettings = wx.Menu()
        self.menuSettingsPanel = self.menuSettings.AppendCheckItem(wx.NewId(), _("Panel"))
        self.menuSettingsVideo = self.menuSettings.AppendCheckItem(wx.NewId(), _("Video"))
        menuView.AppendMenu(wx.NewId(), _("Settings"), self.menuSettings)
        self.menuScanning = wx.Menu()
        self.menuScanningVideo = self.menuScanning.AppendCheckItem(wx.NewId(), _("Video"))
        self.menuScanningScene = self.menuScanning.AppendCheckItem(wx.NewId(), _("Scene"))
        menuView.AppendMenu(wx.NewId(), _("Scanning"), self.menuScanning)
        menuBar.Append(menuView, _("View"))

        #-- Menu Help
        menuHelp = wx.Menu()
        menuAbout = menuHelp.Append(wx.ID_ABOUT, _("About"))
        menuWelcome = menuHelp.Append(wx.ID_ANY, _("Welcome"))
        menuBar.Append(menuHelp, _("Help"))

        self.SetMenuBar(menuBar)

        ##-- Create Workbenchs

        self.mainWorkbench = MainWorkbench(self)
        self.controlWorkbench = ControlWorkbench(self)
        self.settingsWorkbench = SettingsWorkbench(self)
        self.scanningWorkbench = ScanningWorkbench(self)
        self.calibrationWorkbench = CalibrationWorkbench(self)

        for workbench in [self.controlWorkbench, self.settingsWorkbench, self.calibrationWorkbench, self.scanningWorkbench]:
            workbench.combo.Clear()
            workbench.combo.Append(self.workbenchList['control'])
            workbench.combo.Append(self.workbenchList['settings'])
            workbench.combo.Append(self.workbenchList['calibration'])
            workbench.combo.Append(self.workbenchList['scanning'])

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.mainWorkbench, 1, wx.ALL|wx.EXPAND, 30)
        sizer.Add(self.controlWorkbench, 1, wx.EXPAND)
        sizer.Add(self.settingsWorkbench, 1, wx.EXPAND)
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

        self.Bind(wx.EVT_MENU, self.onControlPanelClicked, self.menuControlPanel)
        self.Bind(wx.EVT_MENU, self.onControlVideoClicked, self.menuControlVideo)
        self.Bind(wx.EVT_MENU, self.onSettingsPanelClicked, self.menuSettingsPanel)
        self.Bind(wx.EVT_MENU, self.onSettingsVideoClicked, self.menuSettingsVideo)
        self.Bind(wx.EVT_MENU, self.onScanningVideoSceneClicked, self.menuScanningVideo)
        self.Bind(wx.EVT_MENU, self.onScanningVideoSceneClicked, self.menuScanningScene)

        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.onWelcome, menuWelcome)

        self.Bind(wx.EVT_COMBOBOX, self.onComboBoxWorkbenchSelected, self.controlWorkbench.combo)
        self.Bind(wx.EVT_COMBOBOX, self.onComboBoxWorkbenchSelected, self.settingsWorkbench.combo)
        self.Bind(wx.EVT_COMBOBOX, self.onComboBoxWorkbenchSelected, self.calibrationWorkbench.combo)
        self.Bind(wx.EVT_COMBOBOX, self.onComboBoxWorkbenchSelected, self.scanningWorkbench.combo)

        self.updateProfileToAllControls()

        self.Show()

    def onLoadModel(self, event):
        dlg=wx.FileDialog(self, _("Open 3D model"), os.path.split(profile.getPreference('lastFile'))[0], style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        wildcardFilter = "All (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        wildcardFilter += "|Mesh files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        dlg.SetWildcard(wildcardFilter)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if filename is not None:
                profile.putPreference('lastFile', filename)
                self.scanningWorkbench.sceneView.loadFile(filename)
        dlg.Destroy()

    def onSaveModel(self, event):
        import platform
        if self.scanningWorkbench.sceneView._object is None:
            return
        dlg=wx.FileDialog(self, _("Save 3D model"), os.path.split(profile.getPreference('lastFile'))[0], style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        fileExtensions = meshLoader.saveSupportedExtensions()
        wildcardList = ';'.join(map(lambda s: '*' + s, fileExtensions))
        wildcardFilter = "Mesh files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        dlg.SetWildcard(wildcardFilter)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if platform.system() == 'Linux': #hack for linux, as for some reason the .ini is not appended.
                filename += '.ply'
            meshLoader.saveMesh(filename, self.scanningWorkbench.sceneView._object)
        dlg.Destroy()

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
        self.updateScannerProfile()

    def onControlPanelClicked(self, event):
        """ """
        checked = self.menuControlPanel.IsChecked()
        profile.putPreference('view_control_panel', checked)
        if checked:
            self.controlWorkbench.scrollPanel.Show()
        else:
            self.controlWorkbench.scrollPanel.Hide()
        self.Layout()

    def onControlVideoClicked(self, event):
        """ """
        checked = self.menuControlVideo.IsChecked()
        profile.putPreference('view_control_video', checked)
        if checked:
            self.controlWorkbench.videoView.Show()
        else:
            self.controlWorkbench.videoView.Hide()
        self.Layout()

    def onSettingsPanelClicked(self, event):
        """ """
        checked = self.menuSettingsPanel.IsChecked()
        profile.putPreference('view_settings_panel', checked)
        if checked:
            self.settingsWorkbench.scrollPanel.Show()
        else:
            self.settingsWorkbench.scrollPanel.Hide()
        self.Layout()

    def onSettingsVideoClicked(self, event):
        """ """
        checked = self.menuSettingsVideo.IsChecked()
        profile.putPreference('view_settings_video', checked)
        if checked:
            self.settingsWorkbench.videoView.Show()
        else:
            self.settingsWorkbench.videoView.Hide()
        self.Layout()

    def onScanningVideoSceneClicked(self, event):
        """ """
        checkedVideo = self.menuScanningVideo.IsChecked()
        checkedScene = self.menuScanningScene.IsChecked()
        profile.putPreference('view_scanning_video', checkedVideo)
        profile.putPreference('view_scanning_scene', checkedScene)
        self.scanningWorkbench.splitterWindow.Unsplit()
        if checkedVideo:
            self.scanningWorkbench.videoView.Show()
            self.scanningWorkbench.splitterWindow.SplitVertically(self.scanningWorkbench.videoView, self.scanningWorkbench.sceneView)
            if checkedScene:
                self.scanningWorkbench.sceneView.Show()
            else:
                self.scanningWorkbench.sceneView.Hide()
                self.scanningWorkbench.splitterWindow.Unsplit()
        else:
            self.scanningWorkbench.videoView.Hide()
            if checkedScene:
                self.scanningWorkbench.sceneView.Show()
                self.scanningWorkbench.splitterWindow.SplitVertically(self.scanningWorkbench.sceneView, self.scanningWorkbench.videoView)
                self.scanningWorkbench.splitterWindow.Unsplit()
            else:
                self.scanningWorkbench.sceneView.Hide()
                self.scanningWorkbench.splitterWindow.Unsplit()
                
        self.Layout()

    def onComboBoxWorkbenchSelected(self, event):
        """ """
        for key in self.workbenchList:
            if self.workbenchList[key] == str(event.GetEventObject().GetValue()):
                if key is not None:
                    profile.putPreference('workbench', key)
                else:
                    profile.putPreference('workbench', 'main')
                self.workbenchUpdate()

    def onAbout(self, event):
        """ """
        info = wx.AboutDialogInfo()
        icon = wx.Icon(resources.getPathForImage("horus.ico"), wx.BITMAP_TYPE_ICO)
        info.SetIcon(icon)
        info.SetName(u'Horus')
        info.SetVersion(u'0.0.2')
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

    def onWelcome(self, event):
        """ """
        profile.putPreference('workbench', 'main')
        self.workbenchUpdate()

    def updateProfileToAllControls(self):
        """ """
        self.controlWorkbench.updateProfileToAllControls()
        self.calibrationWorkbench.updateProfileToAllControls()
        self.scanningWorkbench.updateProfileToAllControls()

        if profile.getPreferenceBool('view_control_panel'):
            self.controlWorkbench.scrollPanel.Show()
            self.menuControlPanel.Check(True)
        else:
            self.controlWorkbench.scrollPanel.Hide()
            self.menuControlPanel.Check(False)

        if profile.getPreferenceBool('view_control_video'):
            self.controlWorkbench.videoView.Show()
            self.menuControlVideo.Check(True)
        else:
            self.controlWorkbench.videoView.Hide()
            self.menuControlVideo.Check(False)

        if profile.getPreferenceBool('view_settings_panel'):
            self.settingsWorkbench.scrollPanel.Show()
            self.menuSettingsPanel.Check(True)
        else:
            self.settingsWorkbench.scrollPanel.Hide()
            self.menuSettingsPanel.Check(False)

        if profile.getPreferenceBool('view_settings_video'):
            self.settingsWorkbench.videoView.Show()
            self.menuSettingsVideo.Check(True)
        else:
            self.settingsWorkbench.videoView.Hide()
            self.menuSettingsVideo.Check(False)

        checkedVideo = profile.getPreferenceBool('view_scanning_video')
        checkedScene = profile.getPreferenceBool('view_scanning_scene')

        self.menuScanningVideo.Check(checkedVideo)
        self.menuScanningScene.Check(checkedScene)

        self.scanningWorkbench.splitterWindow.Unsplit()
        if checkedVideo:
            self.scanningWorkbench.videoView.Show()
            self.scanningWorkbench.splitterWindow.SplitVertically(self.scanningWorkbench.videoView, self.scanningWorkbench.sceneView)
            if checkedScene:
                self.scanningWorkbench.sceneView.Show()
            else:
                self.scanningWorkbench.sceneView.Hide()
                self.scanningWorkbench.splitterWindow.Unsplit()
        else:
            self.scanningWorkbench.videoView.Hide()
            if checkedScene:
                self.scanningWorkbench.sceneView.Show()
                self.scanningWorkbench.splitterWindow.SplitVertically(self.scanningWorkbench.sceneView, self.scanningWorkbench.videoView)
                self.scanningWorkbench.splitterWindow.Unsplit()
            else:
                self.scanningWorkbench.sceneView.Hide()
                self.scanningWorkbench.splitterWindow.Unsplit()

        self.workbenchUpdate()
        self.Layout()

    def updateEngineProfile(self):
        self.updateScannerProfile()
        #self.updateCoreCurrentProfile()
        #self.updateCameraCurrentProfile()
        self.updateCalibrationCurrentProfile()

    def updateScannerProfile(self):
        self.scanner.initialize(int(profile.getProfileSetting('camera_id')[-1:]),
                                profile.getProfileSetting('serial_name'))

    def updateCameraCurrentProfile(self):
        self.updateCameraProfile(profile.getPreference('workbench'))

    def updateCameraProfile(self, workbench):
        if workbench in ['control', 'calibration', 'scanning']:
            self.scanner.camera.initialize(profile.getProfileSettingInteger('brightness_' + workbench),
                                           profile.getProfileSettingInteger('contrast_' + workbench),
                                           profile.getProfileSettingInteger('saturation_' + workbench),
                                           profile.getProfileSettingInteger('exposure_' + workbench),
                                           profile.getProfileSettingInteger('framerate_' + workbench),
                                           profile.getProfileSettingInteger('camera_width_' + workbench),
                                           profile.getProfileSettingInteger('camera_height_' + workbench),
                                           profile.getProfileSettingNumpy('camera_matrix'),
                                           profile.getProfileSettingNumpy('distortion_vector'),
                                           profile.getProfileSettingInteger('use_distortion_' + workbench))

            self.scanner.core.setResolution(profile.getProfileSettingInteger('camera_height_scanning'),
                                            profile.getProfileSettingInteger('camera_width_scanning'))

    def updateCoreCurrentProfile(self):
        self.updateCoreProfile(profile.getPreference('workbench'))

    def updateCoreProfile(self, workbench):
        if workbench in ['settings', 'scanning']:
            self.scanner.core.initialize(profile.getProfileSetting('img_type'),
                                         profile.getProfileSettingBool('open'),
                                         profile.getProfileSettingInteger('open_value'),
                                         profile.getProfileSettingBool('threshold'),
                                         profile.getProfileSettingInteger('threshold_value'),
                                         profile.getProfileSettingBool('use_compact'),
                                         profile.getProfileSettingInteger('min_rho'),
                                         profile.getProfileSettingInteger('max_rho'),
                                         profile.getProfileSettingInteger('min_h'),
                                         profile.getProfileSettingInteger('max_h'),
                                         profile.getProfileSettingFloat('step_degrees_scanning'),
                                         profile.getProfileSettingInteger('camera_height_scanning'),
                                         profile.getProfileSettingInteger('camera_width_scanning'),
                                         profile.getProfileSettingFloat('laser_angle'),
                                         profile.getProfileSettingNumpy('camera_matrix'),
                                         profile.getProfileSettingNumpy('laser_coordinates'),
                                         profile.getProfileSettingNumpy('laser_depth'),
                                         profile.getProfileSettingNumpy('rotation_matrix'),
                                         profile.getProfileSettingNumpy('translation_vector'))
    
    def updateCalibrationCurrentProfile(self):
        self.updateCalibrationProfile(profile.getPreference('workbench'))

    def updateCalibrationProfile(self, workbench):
        if workbench in ['settings', 'calibration']:
            self.calibration.initialize(profile.getProfileSettingNumpy('camera_matrix'),
                                        profile.getProfileSettingNumpy('distortion_vector'),
                                        profile.getProfileSettingInteger('pattern_rows'),
                                        profile.getProfileSettingInteger('pattern_columns'),
                                        profile.getProfileSettingInteger('square_width'),
                                        profile.getProfileSettingInteger('use_distortion_calibration'))

    def updateFirmware(self):
        avr_dude = AvrDude(port=profile.getProfileSetting('serial_name'))
        stdout, stderr = avr_dude.flash(hex_path=resources.getPathForFirmware("eeprom_clear.hex"), extra_flags=["-D"])
        print stdout
        print stderr
        time.sleep(4) #-- time to clear eeprom
        stdout, stderr = avr_dude.flash(hex_path=resources.getPathForFirmware("horus.hex"), extra_flags=["-D"])
        print stdout
        print stderr

    def workbenchUpdate(self):
        """ """
        currentWorkbench = profile.getPreference('workbench')

        wb = {'main'        : self.mainWorkbench, 
              'control'     : self.controlWorkbench,
              'settings'    : self.settingsWorkbench,
              'calibration' : self.calibrationWorkbench,
              'scanning'    : self.scanningWorkbench}

        if currentWorkbench == 'settings':
            self.scanner.moveMotor = False
            self.scanner.generatePointCloud = False
        else:
            self.scanner.moveMotor = True
            self.scanner.generatePointCloud = True

        for key in wb:
            if wb[key] is not None:
                if key == currentWorkbench:
                    wb[key].Show()
                    if key is not 'main':
                        wb[key].combo.SetValue(str(self.workbenchList[key]))
                else:
                    wb[key].Hide()

        self.menuFile.Enable(self.menuLoadModel.GetId(), currentWorkbench == 'scanning')
        self.menuFile.Enable(self.menuSaveModel.GetId(), currentWorkbench == 'scanning')
        self.menuFile.Enable(self.menuClearModel.GetId(), currentWorkbench == 'scanning')

        self.updateCameraProfile(currentWorkbench)
        self.updateCoreProfile(currentWorkbench)
        self.updateCalibrationProfile(currentWorkbench)

        self.Layout()


    ##-- TODO: move to util

    def serialList(self):
        baselist=[]
        if os.name=="nt":
            import _winreg
            try:
                key=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"HARDWARE\\DEVICEMAP\\SERIALCOMM")
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
            for device in ['/dev/ttyACM*', '/dev/ttyUSB*', "/dev/tty.usb*", "/dev/cu.*", "/dev/rfcomm*"]:
                baselist = baselist + glob.glob(device)
        return baselist

    def videoList(self):
        baselist=[]
        if os.name=="nt":
            for i in range(10):
                cap = cv2.VideoCapture(i)
                if not cap.isOpened():
                    break
                cap.release()
                baselist.append(str(i))
        else:
            for device in ['/dev/video*']:
                baselist = baselist + glob.glob(device)
        return baselist

    ##-- END TODO

from horus.gui.util.imageView import *

class MainWorkbench(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)
        titleBox = wx.BoxSizer(wx.VERTICAL)
        panelBox = wx.BoxSizer(wx.HORIZONTAL)

        self._title = wx.Panel(self)
        self._panel = wx.Panel(self)
        self._controlPanel = ItemWorkbench(self._panel, label=_("Control"), image=wx.Image(resources.getPathForImage("control.png")))
        self._settingsPanel = ItemWorkbench(self._panel, label=_("Settings"), image=wx.Image(resources.getPathForImage("settings.png")))
        self._calibrationPanel = ItemWorkbench(self._panel, label=_("Calibration"), image=wx.Image(resources.getPathForImage("calibration.png")))
        self._scanningPanel = ItemWorkbench(self._panel, label=_("Scanning"), image=wx.Image(resources.getPathForImage("scanning.png")))

        logo = ImageView(self._title)
        logo.setImage(wx.Image(resources.getPathForImage("logo.png")))
        titleText = wx.StaticText(self._title, label=_("3D scanning for everyone"))
        titleText.SetFont((wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_LIGHT)))
        separator = wx.StaticLine(self._title, -1, style=wx.LI_HORIZONTAL)

        titleBox.Add(logo, 3, wx.ALL^wx.BOTTOM|wx.EXPAND, 30)
        titleBox.Add(titleText, 0, wx.ALL|wx.CENTER, 20)
        titleBox.Add((0,0), 1, wx.ALL|wx.EXPAND, 2)
        titleBox.Add(separator, 0, wx.ALL|wx.EXPAND, 10)
        self._title.SetSizer(titleBox)

        panelBox.Add(self._controlPanel, 1, wx.ALL|wx.EXPAND, 20)
        panelBox.Add(self._settingsPanel, 1, wx.ALL|wx.EXPAND, 20)
        panelBox.Add(self._calibrationPanel, 1, wx.ALL|wx.EXPAND, 20)
        panelBox.Add(self._scanningPanel, 1, wx.ALL|wx.EXPAND, 20)
        self._panel.SetSizer(panelBox)

        vbox.Add(self._title, 7, wx.ALL|wx.EXPAND, 2)
        vbox.Add((0,0), 1, wx.ALL|wx.EXPAND, 0)
        vbox.Add(self._panel, 7, wx.ALL|wx.EXPAND, 2)

        self._controlPanel.imageView.Bind(wx.EVT_LEFT_UP, self.onWorkbenchSelected)
        self._settingsPanel.imageView.Bind(wx.EVT_LEFT_UP, self.onWorkbenchSelected)
        self._calibrationPanel.imageView.Bind(wx.EVT_LEFT_UP, self.onWorkbenchSelected)
        self._scanningPanel.imageView.Bind(wx.EVT_LEFT_UP, self.onWorkbenchSelected)

        self.SetSizer(vbox)
        self.Layout()

    def onWorkbenchSelected(self, event):
        """ """
        currentWorkbench = {self._controlPanel.imageView.GetId()     : 'control',
                            self._settingsPanel.imageView.GetId()    : 'settings',
                            self._calibrationPanel.imageView.GetId() : 'calibration',
                            self._scanningPanel.imageView.GetId()    : 'scanning'}.get(event.GetId())

        if currentWorkbench is not None:
            profile.putPreference('workbench', currentWorkbench)
        else:
            profile.putPreference('workbench', 'main')

        self.GetParent().workbenchUpdate()


class ItemWorkbench(wx.Panel):

    def __init__(self, parent, label="Workbench", image=None):
        wx.Panel.__init__(self, parent)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.imageView = ImageView(self)
        self.imageView.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        if image is not None:
            self.imageView.setImage(image)
        labelText = wx.StaticText(self, label=label)
        labelText.SetFont((wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)))

        vbox.Add(self.imageView, 1, wx.ALL|wx.EXPAND, 10)
        vbox.Add(labelText, 0, wx.CENTER, 20)

        self.SetSizer(vbox)
        self.Layout()