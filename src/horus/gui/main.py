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

import os
import wx._core

from horus.util.profile import *
from horus.util.resources import *
from horus.util.meshLoader import *

from horus.gui.workbench.control.main import ControlWorkbench
from horus.gui.workbench.scanning.main import ScanningWorkbench
from horus.gui.workbench.calibration.main import CalibrationWorkbench
from horus.gui.preferences import PreferencesDialog
from horus.gui.welcome import WelcomeWindow

from horus.engine.scanner import *
from horus.engine.calibration import *

VERSION = "0.0.4.1"

class MainWindow(wx.Frame):

    def __init__(self):
        super(MainWindow, self).__init__(None, title=_("Horus " + VERSION),
                                                size=(640+300,480+130))

        self.SetMinSize((600, 450))

        ###-- Initialize Engine

        #-- Serial Name initialization
        serialList = self.serialList()
        currentSerial = getProfileSetting('serial_name')
        if len(serialList) > 0:
            if currentSerial not in serialList:
                putProfileSetting('serial_name', serialList[0])

        #-- Video Id initialization
        videoList = self.videoList()
        currentVideoId = getProfileSetting('camera_id')
        if len(videoList) > 0:
            if currentVideoId not in videoList:
                putProfileSetting('camera_id', videoList[0])

        self.workbenchList = {'control'     : _("Control workbench"),
                              'calibration' : _("Calibration workbench"),
                              'scanning'    : _("Scanning workbench")}

        self.lastFiles = eval(getPreference('last_files'))
            
        self.scanner = Scanner.Instance()
        self.calibration = Calibration.Instance()

        self.updateEngineProfile()

        ###-- Initialize GUI

        ##-- Set Icon
        icon = wx.Icon(getPathForImage("horus.ico"), wx.BITMAP_TYPE_ICO)
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
        self.menuBasicMode = self.menuEdit.AppendRadioItem(wx.NewId(), _("Basic Mode"))
        self.menuAdvancedMode = self.menuEdit.AppendRadioItem(wx.NewId(), _("Advanced Mode"))
        self.menuEdit.AppendSeparator()
        self.menuPreferences = self.menuEdit.Append(wx.NewId(), _("Preferences"))
        menuBar.Append(self.menuEdit, _("Edit"))

        #-- Menu View
        menuView = wx.Menu()
        self.menuControl = wx.Menu()
        self.menuControlPanel = self.menuControl.AppendCheckItem(wx.NewId(), _("Panel"))
        self.menuControlVideo = self.menuControl.AppendCheckItem(wx.NewId(), _("Video"))
        menuView.AppendMenu(wx.NewId(), _("Control"), self.menuControl)
        self.menuCalibration = wx.Menu()
        self.menuCalibrationPanel = self.menuCalibration.AppendCheckItem(wx.NewId(), _("Panel"))
        self.menuCalibrationVideo = self.menuCalibration.AppendCheckItem(wx.NewId(), _("Video"))
        menuView.AppendMenu(wx.NewId(), _("Calibration"), self.menuCalibration)
        self.menuScanning = wx.Menu()
        self.menuScanningPanel = self.menuScanning.AppendCheckItem(wx.NewId(), _("Panel"))
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
        self.controlWorkbench = ControlWorkbench(self)
        self.scanningWorkbench = ScanningWorkbench(self)
        self.calibrationWorkbench = CalibrationWorkbench(self)

        for workbench in [self.controlWorkbench, self.calibrationWorkbench, self.scanningWorkbench]:
            workbench.combo.Clear()
            workbench.combo.Append(self.workbenchList['control'])
            workbench.combo.Append(self.workbenchList['calibration'])
            workbench.combo.Append(self.workbenchList['scanning'])

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.controlWorkbench, 1, wx.ALL|wx.EXPAND)
        sizer.Add(self.calibrationWorkbench, 1, wx.ALL|wx.EXPAND)
        sizer.Add(self.scanningWorkbench, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer)

        ##-- Events
        self.Bind(wx.EVT_MENU, self.onLoadModel, self.menuLoadModel)
        self.Bind(wx.EVT_MENU, self.onSaveModel, self.menuSaveModel)
        self.Bind(wx.EVT_MENU, self.onClearModel, self.menuClearModel)
        self.Bind(wx.EVT_MENU, self.onOpenProfile, menuOpenProfile)
        self.Bind(wx.EVT_MENU, self.onSaveProfile, menuSaveProfile)
        self.Bind(wx.EVT_MENU, self.onResetProfile, menuResetProfile)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)

        self.Bind(wx.EVT_MENU, self.onModeChanged, self.menuBasicMode)
        self.Bind(wx.EVT_MENU, self.onModeChanged, self.menuAdvancedMode)
        self.Bind(wx.EVT_MENU, self.onPreferences, self.menuPreferences)

        self.Bind(wx.EVT_MENU, self.onControlPanelClicked, self.menuControlPanel)
        self.Bind(wx.EVT_MENU, self.onControlVideoClicked, self.menuControlVideo)
        self.Bind(wx.EVT_MENU, self.onCalibrationPanelClicked, self.menuCalibrationPanel)
        self.Bind(wx.EVT_MENU, self.onCalibrationVideoClicked, self.menuCalibrationVideo)
        self.Bind(wx.EVT_MENU, self.onScanningPanelClicked, self.menuScanningPanel)
        self.Bind(wx.EVT_MENU, self.onScanningVideoSceneClicked, self.menuScanningVideo)
        self.Bind(wx.EVT_MENU, self.onScanningVideoSceneClicked, self.menuScanningScene)

        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.onWelcome, menuWelcome)

        self.Bind(wx.EVT_COMBOBOX, self.onComboBoxWorkbenchSelected, self.controlWorkbench.combo)
        self.Bind(wx.EVT_COMBOBOX, self.onComboBoxWorkbenchSelected, self.calibrationWorkbench.combo)
        self.Bind(wx.EVT_COMBOBOX, self.onComboBoxWorkbenchSelected, self.scanningWorkbench.combo)

        self.updateProfileToAllControls()

        self.Center()
        self.Show()

    def onLoadModel(self, event):
        lastFile = os.path.split(getPreference('last_file'))[0]
        dlg = wx.FileDialog(self, _("Open 3D model"), lastFile, style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        wildcardList = ';'.join(map(lambda s: '*' + s, loadSupportedExtensions()))
        wildcardFilter = "All (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        wildcardList = ';'.join(map(lambda s: '*' + s, loadSupportedExtensions()))
        wildcardFilter += "|Mesh files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        dlg.SetWildcard(wildcardFilter)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if filename is not None:
                self.scanningWorkbench.sceneView.loadFile(filename)
                self.appendLastFile(filename)
        dlg.Destroy()

    def onSaveModel(self, event):
        import platform
        if self.scanningWorkbench.sceneView._object is None:
            return
        dlg = wx.FileDialog(self, _("Save 3D model"), os.path.split(getPreference('last_file'))[0], style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        fileExtensions = saveSupportedExtensions()
        wildcardList = ';'.join(map(lambda s: '*' + s, fileExtensions))
        wildcardFilter = "Mesh files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        dlg.SetWildcard(wildcardFilter)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not filename.endswith('.ply'):
                if platform.system() == 'Linux': #hack for linux, as for some reason the .ply is not appended.
                    filename += '.ply'
            saveMesh(filename, self.scanningWorkbench.sceneView._object)
            self.appendLastFile(filename)
        dlg.Destroy()

    def onClearModel(self, event):
        if self.scanningWorkbench.sceneView._object is not None:
            dlg = wx.MessageDialog(self, _("Your current model will be erased.\nDo you really want to do it?"), _("Clear Point Cloud"), wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()
            if result:
                self.scanningWorkbench.sceneView._clearScene()

    def onOpenProfile(self, event):
        """ """
        dlg=wx.FileDialog(self, _("Select profile file to load"), os.path.split(getPreference('last_profile'))[0], style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        dlg.SetWildcard("ini files (*.ini)|*.ini")
        if dlg.ShowModal() == wx.ID_OK:
            profileFile = dlg.GetPath()
            loadProfile(profileFile)
            self.updateProfileToAllControls()
        dlg.Destroy()

    def onSaveProfile(self, event):
        """ """
        import platform
        dlg=wx.FileDialog(self, _("Select profile file to save"), os.path.split(getPreference('last_profile'))[0], style=wx.FD_SAVE)
        dlg.SetWildcard("ini files (*.ini)|*.ini")
        if dlg.ShowModal() == wx.ID_OK:
            profileFile = dlg.GetPath()
            if not profileFile.endswith('.ini'):
                if platform.system() == 'Linux': #hack for linux, as for some reason the .ini is not appended.
                    profileFile += '.ini'
            saveProfile(profileFile)
        dlg.Destroy()

    def onResetProfile(self, event):
        """ """
        dlg = wx.MessageDialog(self, _("This will reset all profile settings to defaults.\nUnless you have saved your current profile, all settings will be lost!\nDo you really want to reset?"), _("Profile reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            resetProfile()
            self.updateProfileToAllControls()

    def onExit(self, event):
        self.Close(True)

    def appendLastFile(self, lastFile):
        if lastFile in self.lastFiles:
            self.lastFiles.remove(lastFile)
        self.lastFiles.append(lastFile)
        if len(self.lastFiles) > 4:
            self.lastFiles = self.lastFiles[1:5]
        putPreference('last_file', lastFile)
        putPreference('last_files', self.lastFiles)

    def onModeChanged(self, event):
        putPreference('basic_mode', self.menuBasicMode.IsChecked())
        self.controlWorkbench.updateProfileToAllControls()
        self.calibrationWorkbench.updateProfileToAllControls()
        self.scanningWorkbench.updateProfileToAllControls()
        self.Layout()

    def onPreferences(self, event):
        prefDialog = PreferencesDialog(self)
        prefDialog.ShowModal()
        wx.CallAfter(prefDialog.Show)
        self.updateScannerProfile()
        self.controlWorkbench.initialize()
        self.calibrationWorkbench.initialize()

    def onControlPanelClicked(self, event):
        """ """
        checked = self.menuControlPanel.IsChecked()
        putPreference('view_control_panel', checked)
        if checked:
            self.controlWorkbench.scrollPanel.Show()
        else:
            self.controlWorkbench.scrollPanel.Hide()
        self.Layout()

    def onControlVideoClicked(self, event):
        """ """
        checked = self.menuControlVideo.IsChecked()
        putPreference('view_control_video', checked)
        if checked:
            self.controlWorkbench.videoView.Show()
        else:
            self.controlWorkbench.videoView.Hide()
        self.Layout()

    def onCalibrationPanelClicked(self, event):
        """ """
        checked = self.menuCalibrationPanel.IsChecked()
        putPreference('view_calibration_panel', checked)
        if checked:
            self.calibrationWorkbench.scrollPanel.Show()
        else:
            self.calibrationWorkbench.scrollPanel.Hide()
        self.Layout()

    def onCalibrationVideoClicked(self, event):
        """ """
        checked = self.menuCalibrationVideo.IsChecked()
        putPreference('view_calibration_video', checked)
        if checked:
            self.calibrationWorkbench.videoView.Show()
        else:
            self.calibrationWorkbench.videoView.Hide()
        self.Layout()

    def onScanningPanelClicked(self, event):
        checkedPanel = self.menuScanningPanel.IsChecked()
        putPreference('view_scanning_panel', checkedPanel)
        if checkedPanel:
            self.scanningWorkbench.scrollPanel.Show()
        else:
            self.scanningWorkbench.scrollPanel.Hide()
        self.Layout()

    def onScanningVideoSceneClicked(self, event):
        """ """
        checkedVideo = self.menuScanningVideo.IsChecked()
        checkedScene = self.menuScanningScene.IsChecked()
        putPreference('view_scanning_video', checkedVideo)
        putPreference('view_scanning_scene', checkedScene)
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
                    putPreference('workbench', key)
                self.workbenchUpdate()

    def onAbout(self, event):
        """ """
        info = wx.AboutDialogInfo()
        icon = wx.Icon(getPathForImage("horus.ico"), wx.BITMAP_TYPE_ICO)
        info.SetIcon(icon)
        info.SetName(u'Horus')
        info.SetVersion(VERSION)
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
        welcome = WelcomeWindow(self)

    def updateProfileToAllControls(self):
        """ """
        self.controlWorkbench.updateProfileToAllControls()
        self.calibrationWorkbench.updateProfileToAllControls()
        self.scanningWorkbench.updateProfileToAllControls()

        if getPreferenceBool('basic_mode'):
            self.menuBasicMode.Check(True)
        else:
            self.menuAdvancedMode.Check(True)

        if getPreferenceBool('view_control_panel'):
            self.controlWorkbench.scrollPanel.Show()
            self.menuControlPanel.Check(True)
        else:
            self.controlWorkbench.scrollPanel.Hide()
            self.menuControlPanel.Check(False)

        if getPreferenceBool('view_control_video'):
            self.controlWorkbench.videoView.Show()
            self.menuControlVideo.Check(True)
        else:
            self.controlWorkbench.videoView.Hide()
            self.menuControlVideo.Check(False)

        if getPreferenceBool('view_calibration_panel'):
            self.calibrationWorkbench.scrollPanel.Show()
            self.menuCalibrationPanel.Check(True)
        else:
            self.calibrationWorkbench.scrollPanel.Hide()
            self.menuCalibrationPanel.Check(False)

        if getPreferenceBool('view_calibration_video'):
            self.calibrationWorkbench.videoView.Show()
            self.menuCalibrationVideo.Check(True)
        else:
            self.calibrationWorkbench.videoView.Hide()
            self.menuCalibrationVideo.Check(False)

        if getPreferenceBool('view_scanning_panel'):
            self.scanningWorkbench.scrollPanel.Show()
            self.menuScanningPanel.Check(True)
        else:
            self.scanningWorkbench.scrollPanel.Hide()
            self.menuScanningPanel.Check(False)

        checkedVideo = getPreferenceBool('view_scanning_video')
        checkedScene = getPreferenceBool('view_scanning_scene')

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
        self.updateCoreCurrentProfile()
        self.updateCameraCurrentProfile()
        self.updateCalibrationCurrentProfile()

    def updateScannerProfile(self):
        self.scanner.initialize(int(getProfileSetting('camera_id')[-1:]),
                                getProfileSetting('serial_name'))

    def updateDeviceCurrentProfile(self):
        self.updateDeviceProfile(getPreference('workbench'))

    def updateDeviceProfile(self, workbench):
        if workbench in ['control', 'scanning']:
            self.scanner.device.setRelativePosition(getProfileSettingInteger('step_degrees_' + workbench))
            self.scanner.device.setSpeedMotor(getProfileSettingInteger('feed_rate_' + workbench))
            self.scanner.device.setAccelerationMotor(getProfileSettingInteger('acceleration_' + workbench))

    def updateCameraCurrentProfile(self):
        self.updateCameraProfile(getPreference('workbench'))

    def updateCameraProfile(self, workbench):
        if workbench in ['control', 'calibration', 'scanning']:
            self.scanner.camera.setBrightness(getProfileSettingInteger('brightness_' + workbench))
            self.scanner.camera.setContrast(getProfileSettingInteger('contrast_' + workbench))
            self.scanner.camera.setSaturation(getProfileSettingInteger('saturation_' + workbench))
            self.scanner.camera.setExposure(getProfileSettingInteger('exposure_' + workbench))
            self.scanner.camera.setFrameRate(getProfileSettingInteger('framerate_' + workbench))
            resolution = getProfileSetting('resolution_' + workbench)
            self.scanner.camera.setResolution(int(resolution.split('x')[0]), int(resolution.split('x')[1]))
            self.scanner.camera.setUseDistortion(getProfileSettingBool('use_distortion_' + workbench))
            self.scanner.camera.setIntrinsics(getProfileSettingNumpy('camera_matrix'),
                                              getProfileSettingNumpy('distortion_vector'))

    def updateCoreCurrentProfile(self):
        self.updateCoreProfile(getPreference('workbench'))

    def updateCoreProfile(self, workbench):
        if workbench in ['scanning']:
            self.scanner.core.resetTheta()
            self.scanner.core.setImageType(getProfileSetting('img_type'))
            self.scanner.core.setUseOpen(getProfileSettingBool('use_open'))
            self.scanner.core.setOpenValue(getProfileSettingInteger('open_value'))
            self.scanner.core.setUseThreshold(getProfileSettingBool('use_threshold'))
            self.scanner.core.setThresholdValue(getProfileSettingInteger('threshold_value'))
            self.scanner.core.setUseCompact(getProfileSettingBool('use_compact'))
            self.scanner.core.setMinR(getProfileSettingInteger('min_r'))
            self.scanner.core.setMaxR(getProfileSettingInteger('max_r'))
            self.scanner.core.setMinH(getProfileSettingInteger('min_h'))
            self.scanner.core.setMaxH(getProfileSettingInteger('max_h'))
            self.scanner.core.setDegrees(getProfileSettingFloat('step_degrees_scanning'))
            resolution = getProfileSetting('resolution_scanning')
            self.scanner.core.setResolution(int(resolution.split('x')[1]), int(resolution.split('x')[0]))
            self.scanner.core.setUseLaser(getProfileSetting('use_laser')==_("Use Left Laser"),
                                          getProfileSetting('use_laser')==_("Use Right Laser"))
            self.scanner.core.setLaserAngles(getProfileSettingFloat('laser_angle_left'),
                                             getProfileSettingFloat('laser_angle_right'))
            self.scanner.core.setIntrinsics(getProfileSettingNumpy('camera_matrix'),
                                            getProfileSettingNumpy('distortion_vector'))
            self.scanner.core.setLaserTriangulation(getProfileSettingNumpy('laser_coordinates'),
                                                    getProfileSettingNumpy('laser_origin'),
                                                    getProfileSettingNumpy('laser_normal'))
            self.scanner.core.setExtrinsics(getProfileSettingNumpy('rotation_matrix'),
                                            getProfileSettingNumpy('translation_vector'))
    
    def updateCalibrationCurrentProfile(self):
        self.updateCalibrationProfile(getPreference('workbench'))

    def updateCalibrationProfile(self, workbench):
        if workbench in ['calibration']:
            self.calibration.initialize(getProfileSettingNumpy('camera_matrix'),
                                        getProfileSettingNumpy('distortion_vector'),
                                        getProfileSettingInteger('pattern_rows'),
                                        getProfileSettingInteger('pattern_columns'),
                                        getProfileSettingInteger('square_width'),
                                        getProfileSettingFloat('pattern_distance'),
                                        getProfileSettingFloat('extrinsics_step'),
                                        getProfileSettingInteger('use_distortion_calibration'))

    def workbenchUpdate(self):
        """ """

        #TODO: optimize load

        currentWorkbench = getPreference('workbench')
        putPreference('workbench', 'scanning') ##TODO: force save scanning workbench

        wb = {'control'     : self.controlWorkbench,
              'calibration' : self.calibrationWorkbench,
              'scanning'    : self.scanningWorkbench}

        self.scanner.moveMotor = True
        self.scanner.generatePointCloud = True

        for key in wb:
            if wb[key] is not None:
                if key == currentWorkbench:
                    wb[key].Show()
                    wb[key].updateProfileToAllControls()
                    wb[key].combo.SetValue(str(self.workbenchList[key]))
                else:
                    wb[key].Hide()

        self.menuFile.Enable(self.menuLoadModel.GetId(), currentWorkbench == 'scanning')
        self.menuFile.Enable(self.menuSaveModel.GetId(), currentWorkbench == 'scanning')
        self.menuFile.Enable(self.menuClearModel.GetId(), currentWorkbench == 'scanning')

        self.updateDeviceProfile(currentWorkbench)
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
                    if 'USBSER' in values[0] or 'VCP' in values[0]:
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