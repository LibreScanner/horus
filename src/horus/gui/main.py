# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import gc
import os
import time
import struct
import wx._core
import webbrowser

from horus.gui.workbench.control.main import ControlWorkbench
from horus.gui.workbench.adjustment.main import AdjustmentWorkbench
from horus.gui.workbench.calibration.main import CalibrationWorkbench
from horus.gui.workbench.scanning.main import ScanningWorkbench
from horus.gui.preferences import PreferencesDialog
from horus.gui.machineSettings import MachineSettingsDialog
from horus.gui.welcome import WelcomeWindow
from horus.gui.wizard.main import *
from horus.gui.util.versionWindow import VersionWindow

from horus.engine.driver.driver import Driver
from horus.engine.scan.ciclop_scan import CiclopScan
from horus.engine.scan.current_video import CurrentVideo
from horus.engine.calibration.pattern import Pattern
from horus.engine.calibration.calibration_data import CalibrationData
from horus.engine.calibration.laser_triangulation import LaserTriangulation
from horus.engine.calibration.platform_extrinsics import PlatformExtrinsics
from horus.engine.algorithms.image_capture import ImageCapture
from horus.engine.algorithms.image_detection import ImageDetection
from horus.engine.algorithms.laser_segmentation import LaserSegmentation
from horus.engine.algorithms.point_cloud_generation import PointCloudGeneration
from horus.engine.algorithms.point_cloud_roi import PointCloudROI

from horus.util import profile, resources, meshLoader, version, system as sys

driver = Driver()
ciclop_scan = CiclopScan()
current_video = CurrentVideo()
pattern = Pattern()
calibration_data = CalibrationData()
laser_triangulation = LaserTriangulation()
platform_extrinsics = PlatformExtrinsics()
image_capture = ImageCapture()
image_detection = ImageDetection()
laser_segmentation = LaserSegmentation()
point_cloud_generation = PointCloudGeneration()
point_cloud_roi = PointCloudROI()


class MainWindow(wx.Frame):

    size = (640 + 340, 480 + 155)

    def __init__(self):
        super(MainWindow, self).__init__(None, title=_("Horus 0.2 BETA"), size=self.size)

        self.SetMinSize((600, 450))

        # Serial Name initialization
        serialList = driver.board.get_serial_list()
        currentSerial = profile.settings['serial_name']
        if len(serialList) > 0:
            if currentSerial not in serialList:
                profile.settings['serial_name'] = serialList[0]

        # Video Id initialization
        videoList = driver.camera.get_video_list()
        currentVideoId = profile.settings['camera_id']
        if len(videoList) > 0:
            if currentVideoId not in videoList:
                profile.settings['camera_id'] = unicode(videoList[0])

        self.lastFiles = profile.settings['last_files']

        print ">>> Horus " + version.getVersion() + " <<<"

        # Initialize GUI

        # Set Icon
        icon = wx.Icon(resources.getPathForImage("horus.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        # Status Bar
        # self.CreateStatusBar()

        # Menu Bar
        self.menuBar = wx.MenuBar()

        # Menu File
        self.menuFile = wx.Menu()
        self.menuLaunchWizard = self.menuFile.Append(wx.NewId(), _("Launch Wizard"))
        self.menuFile.AppendSeparator()
        self.menuLoadModel = self.menuFile.Append(wx.NewId(), _("Load Model"))
        self.menuSaveModel = self.menuFile.Append(wx.NewId(), _("Save Model"))
        self.menuClearModel = self.menuFile.Append(wx.NewId(), _("Clear Model"))
        self.menuFile.AppendSeparator()
        self.menuOpenCalibrationProfile = self.menuFile.Append(
            wx.NewId(), _("Open Calibration Profile"), _("Opens Calibration profile .json"))
        self.menuSaveCalibrationProfile = self.menuFile.Append(
            wx.NewId(), _("Save Calibration Profile"), _("Saves Calibration profile .json"))
        self.menuResetCalibrationProfile = self.menuFile.Append(
            wx.NewId(), _("Reset Calibration Profile"), _("Resets Calibration default values"))
        self.menuFile.AppendSeparator()
        self.menuOpenScanProfile = self.menuFile.Append(
            wx.NewId(), _("Open Scan Profile"), _("Opens Scan profile .json"))
        self.menuSaveScanProfile = self.menuFile.Append(
            wx.NewId(), _("Save Scan Profile"), _("Saves Scan profile .json"))
        self.menuResetScanProfile = self.menuFile.Append(
            wx.NewId(), _("Reset Scan Profile"), _("Resets Scan default values"))
        self.menuFile.AppendSeparator()
        self.menuExit = self.menuFile.Append(wx.ID_EXIT, _("Exit"))
        self.menuBar.Append(self.menuFile, _("File"))

        # Menu Edit
        self.menuEdit = wx.Menu()
        self.menuPreferences = self.menuEdit.Append(wx.NewId(), _("Preferences"))
        self.menuMachineSettings = self.menuEdit.Append(wx.NewId(), _("Machine Settings"))
        self.menuBar.Append(self.menuEdit, _("Edit"))

        # Menu View
        self.menuView = wx.Menu()
        self.menuControl = wx.Menu()
        self.menuControlPanel = self.menuControl.AppendCheckItem(wx.NewId(), _("Panel"))
        self.menuControlVideo = self.menuControl.AppendCheckItem(wx.NewId(), _("Video"))
        self.menuView.AppendMenu(wx.NewId(), _("Control"), self.menuControl)
        self.menuAdjustment = wx.Menu()
        self.menuAdjustmentPanel = self.menuAdjustment.AppendCheckItem(wx.NewId(), _("Panel"))
        self.menuAdjustmentVideo = self.menuAdjustment.AppendCheckItem(wx.NewId(), _("Video"))
        self.menuView.AppendMenu(wx.NewId(), _("Adjustment"), self.menuAdjustment)
        self.menuCalibration = wx.Menu()
        self.menuCalibrationPanel = self.menuCalibration.AppendCheckItem(wx.NewId(), _("Panel"))
        self.menuCalibrationVideo = self.menuCalibration.AppendCheckItem(wx.NewId(), _("Video"))
        self.menuView.AppendMenu(wx.NewId(), _("Calibration"), self.menuCalibration)
        self.menuScanning = wx.Menu()
        self.menuScanningPanel = self.menuScanning.AppendCheckItem(wx.NewId(), _("Panel"))
        self.menuScanningVideo = self.menuScanning.AppendCheckItem(wx.NewId(), _("Video"))
        self.menuScanningScene = self.menuScanning.AppendCheckItem(wx.NewId(), _("Scene"))
        self.menuView.AppendMenu(wx.NewId(), _("Scanning"), self.menuScanning)
        self.menuBar.Append(self.menuView, _("View"))

        # Menu Help
        self.menuHelp = wx.Menu()
        self.menuWelcome = self.menuHelp.Append(wx.ID_ANY, _("Welcome"))
        if profile.settings['check_for_updates']:
            self.menuUpdates = self.menuHelp.Append(wx.ID_ANY, _("Updates"))
        self.menuWiki = self.menuHelp.Append(wx.ID_ANY, _("Wiki"))
        self.menuSources = self.menuHelp.Append(wx.ID_ANY, _("Sources"))
        self.menuIssues = self.menuHelp.Append(wx.ID_ANY, _("Issues"))
        self.menuForum = self.menuHelp.Append(wx.ID_ANY, _("Forum"))
        self.menuAbout = self.menuHelp.Append(wx.ID_ABOUT, _("About"))
        self.menuBar.Append(self.menuHelp, _("Help"))

        self.SetMenuBar(self.menuBar)

        # Create Workbenchs
        self.workbench = {}
        self.workbench['control'] = ControlWorkbench(self)
        self.workbench['adjustment'] = AdjustmentWorkbench(self)
        self.workbench['calibration'] = CalibrationWorkbench(self)
        self.workbench['scanning'] = ScanningWorkbench(self)

        _choices = []
        choices = profile.settings.getPossibleValues('workbench')
        for i in choices:
            _choices.append(_(i))
        self.workbenchDict = dict(zip(_choices, choices))

        for w in self.workbench.values():
            w.combo.Clear()
            for i in choices:
                w.combo.Append(_(i))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.workbench['control'], 1, wx.ALL | wx.EXPAND)
        sizer.Add(self.workbench['adjustment'], 1, wx.ALL | wx.EXPAND)
        sizer.Add(self.workbench['calibration'], 1, wx.ALL | wx.EXPAND)
        sizer.Add(self.workbench['scanning'], 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)

        # Events
        self.Bind(wx.EVT_MENU, self.onLaunchWizard, self.menuLaunchWizard)
        self.Bind(wx.EVT_MENU, self.onLoadModel, self.menuLoadModel)
        self.Bind(wx.EVT_MENU, self.onSaveModel, self.menuSaveModel)
        self.Bind(wx.EVT_MENU, self.onClearModel, self.menuClearModel)
        self.Bind(wx.EVT_MENU,
                  lambda e: self.onOpenProfile("calibration_settings"),
                  self.menuOpenCalibrationProfile)
        self.Bind(wx.EVT_MENU,
                  lambda e: self.onSaveProfile("calibration_settings"),
                  self.menuSaveCalibrationProfile)
        self.Bind(wx.EVT_MENU,
                  lambda e: self.onResetProfile("calibration_settings"),
                  self.menuResetCalibrationProfile)
        self.Bind(wx.EVT_MENU,
                  lambda e: self.onOpenProfile("scan_settings"), self.menuOpenScanProfile)
        self.Bind(wx.EVT_MENU,
                  lambda e: self.onSaveProfile("scan_settings"), self.menuSaveScanProfile)
        self.Bind(wx.EVT_MENU,
                  lambda e: self.onResetProfile("scan_settings"), self.menuResetScanProfile)
        self.Bind(wx.EVT_MENU, self.onExit, self.menuExit)
        # self.Bind(wx.EVT_MENU, self.onModeChanged, self.menuBasicMode)
        # self.Bind(wx.EVT_MENU, self.onModeChanged, self.menuAdvancedMode)
        self.Bind(wx.EVT_MENU, self.onPreferences, self.menuPreferences)
        self.Bind(wx.EVT_MENU, self.onMachineSettings, self.menuMachineSettings)

        self.Bind(wx.EVT_MENU, self.onControlPanelClicked, self.menuControlPanel)
        self.Bind(wx.EVT_MENU, self.onControlVideoClicked, self.menuControlVideo)
        self.Bind(wx.EVT_MENU, self.onAdjustmentPanelClicked, self.menuAdjustmentPanel)
        self.Bind(wx.EVT_MENU, self.onAdjustmentVideoClicked, self.menuAdjustmentVideo)
        self.Bind(wx.EVT_MENU, self.onCalibrationPanelClicked, self.menuCalibrationPanel)
        self.Bind(wx.EVT_MENU, self.onCalibrationVideoClicked, self.menuCalibrationVideo)
        self.Bind(wx.EVT_MENU, self.onScanningPanelClicked, self.menuScanningPanel)
        self.Bind(wx.EVT_MENU, self.onScanningVideoSceneClicked, self.menuScanningVideo)
        self.Bind(wx.EVT_MENU, self.onScanningVideoSceneClicked, self.menuScanningScene)

        self.Bind(wx.EVT_MENU, self.onAbout, self.menuAbout)
        self.Bind(wx.EVT_MENU, self.onWelcome, self.menuWelcome)
        if profile.settings['check_for_updates']:
            self.Bind(wx.EVT_MENU, self.onUpdates, self.menuUpdates)
        self.Bind(wx.EVT_MENU, lambda e: webbrowser.open(
            'https://github.com/bq/horus/wiki'), self.menuWiki)
        self.Bind(wx.EVT_MENU, lambda e: webbrowser.open(
            'https://github.com/bq/horus'), self.menuSources)
        self.Bind(wx.EVT_MENU, lambda e: webbrowser.open(
            'https://github.com/bq/horus/issues'), self.menuIssues)
        self.Bind(wx.EVT_MENU, lambda e: webbrowser.open(
            'https://groups.google.com/forum/?hl=es#!forum/ciclop-3d-scanner'), self.menuForum)

        for key in self.workbench.keys():
            self.Bind(wx.EVT_COMBOBOX, self.onComboBoxWorkbenchSelected, self.workbench[key].combo)

        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.updateProfileToAllControls()

        x, y, w, h = wx.Display(0).GetGeometry()
        ws, hs = self.size

        self.SetPosition((x + (w - ws) / 2., y + (h - hs) / 2.))

    def onLaunchWizard(self, event):
        self.workbench['control'].videoView.stop()
        self.workbench['calibration'].videoView.stop()
        self.workbench['calibration'].cameraIntrinsicsMainPage.videoView.stop()
        self.workbench['calibration'].laserTriangulationMainPage.videoView.stop()
        self.workbench['calibration'].platformExtrinsicsMainPage.videoView.stop()
        self.workbench['scanning'].videoView.stop()
        self.workbench['control'].Disable()
        self.workbench['calibration'].Disable()
        self.workbench['scanning'].Disable()
        Wizard(self)
        self.workbench['control'].Enable()
        self.workbench['calibration'].Enable()
        self.workbench['scanning'].Enable()

    def onLoadModel(self, event):
        lastFile = os.path.split(profile.settings['last_file'])[0]
        dlg = wx.FileDialog(
            self, _("Open 3D model"), lastFile, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        wildcardFilter = "All (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        wildcardFilter += "|Mesh files (%s)|%s;%s" % (wildcardList,
                                                      wildcardList, wildcardList.upper())
        dlg.SetWildcard(wildcardFilter)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if filename is not None:
                self.workbench['scanning'].sceneView.loadFile(filename)
                self.appendLastFile(filename)
        dlg.Destroy()

    def onSaveModel(self, event):
        if self.workbench['scanning'].sceneView._object is None:
            return
        dlg = wx.FileDialog(self, _("Save 3D model"), os.path.split(
            profile.settings['last_file'])[0], style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        fileExtensions = meshLoader.saveSupportedExtensions()
        wildcardList = ';'.join(map(lambda s: '*' + s, fileExtensions))
        wildcardFilter = "Mesh files (%s)|%s;%s" % (
            wildcardList, wildcardList, wildcardList.upper())
        dlg.SetWildcard(wildcardFilter)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not filename.endswith('.ply'):
                if sys.isLinux():  # hack for linux, as for some reason the .ply is not appended.
                    filename += '.ply'
            meshLoader.saveMesh(filename, self.workbench['scanning'].sceneView._object)
            self.appendLastFile(filename)
        dlg.Destroy()

    def onClearModel(self, event):
        if self.workbench['scanning'].sceneView._object is not None:
            dlg = wx.MessageDialog(
                self,
                _("Your current model will be erased.\nDo you really want to do it?"),
                _("Clear Point Cloud"), wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()
            if result:
                self.workbench['scanning'].sceneView._clearScene()

    def onOpenProfile(self, category):
        dlg = wx.FileDialog(self, _("Select profile file to load"), profile.getBasePath(),
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        dlg.SetWildcard("JSON files (*.json)|*.json")
        if dlg.ShowModal() == wx.ID_OK:
            profileFile = dlg.GetPath()
            profile.settings.loadSettings(profileFile, categories=[category])
            self.updateProfileToAllControls()
        dlg.Destroy()

    def onSaveProfile(self, category):
        dlg = wx.FileDialog(self, _("Select profile file to save"), profile.getBasePath(),
                            style=wx.FD_SAVE)
        dlg.SetWildcard("JSON files (*.json)|*.json")
        if dlg.ShowModal() == wx.ID_OK:
            profileFile = dlg.GetPath()
            if not profileFile.endswith('.json'):
                if sys.isLinux():  # hack for linux, as for some reason the .json is not appended.
                    profileFile += '.json'
            profile.settings.saveSettings(profileFile, categories=[category])
        dlg.Destroy()

    def onResetProfile(self, category):
        dlg = wx.MessageDialog(
            self,
            _("This will reset all profile settings to defaults.\n"
              "Unless you have saved your current profile, all settings will be lost!\n"
              "Do you really want to reset?"),
            _("Profile reset"), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if result:
            profile.settings.resetToDefault(categories=[category])
            self.updateProfileToAllControls()

    def onExit(self, event):
        self.Close(True)

    def onClose(self, event):
        try:
            driver.board.set_unplug_callback(None)
            driver.camera.set_unplug_callback(None)
            driver.disconnect()
            if ciclop_scan.is_scanning:
                ciclop_scan.stop()
                time.sleep(0.5)
            self.workbench['control'].videoView.stop()
            self.workbench['calibration'].videoView.stop()
            self.workbench['calibration'].cameraIntrinsicsMainPage.videoView.stop()
            self.workbench['calibration'].laserTriangulationMainPage.videoView.stop()
            self.workbench['calibration'].platformExtrinsicsMainPage.videoView.stop()
            self.workbench['scanning'].videoView.stop()
        except:
            pass
        event.Skip()

    def appendLastFile(self, lastFile):
        if lastFile in self.lastFiles:
            self.lastFiles.remove(lastFile)
        self.lastFiles.append(lastFile)
        if len(self.lastFiles) > 4:
            self.lastFiles = self.lastFiles[1:5]
        profile.settings['last_file'] = lastFile
        profile.settings['last_files'] = self.lastFiles

    def onModeChanged(self, event):
        # profile.settings['basic_mode'] = self.menuBasicMode.IsChecked()
        self.workbench['control'].updateProfileToAllControls()
        self.workbench['adjustment'].updateProfileToAllControls()
        self.workbench['calibration'].updateProfileToAllControls()
        self.workbench['scanning'].updateProfileToAllControls()
        self.Layout()

    def onPreferences(self, event):
        if sys.isWindows():
            ciclop_scan.stop()
            laser_triangulation.cancel()
            platform_extrinsics.cancel()
            self.workbench['control'].videoView.stop()
            self.workbench['calibration'].videoView.stop()
            self.workbench['calibration'].cameraIntrinsicsMainPage.videoView.stop()
            self.workbench['calibration'].laserTriangulationMainPage.videoView.stop()
            self.workbench['calibration'].platformExtrinsicsMainPage.videoView.stop()
            self.workbench['scanning'].videoView.stop()
            driver.board.set_unplug_callback(None)
            driver.camera.set_unplug_callback(None)
            self.workbench['control'].updateStatus(False)
            self.workbench['calibration'].updateStatus(False)
            self.workbench['scanning'].updateStatus(False)
            driver.disconnect()
            # waitCursor = wx.BusyCursor()

        prefDialog = PreferencesDialog()
        prefDialog.ShowModal()

        self.updateDriverProfile()
        self.workbench['control'].updateCallbacks()
        self.workbench['adjustment'].updateCallbacks()
        self.workbench['calibration'].updateCallbacks()
        self.workbench['scanning'].updateCallbacks()

    def onMachineSettings(self, event):
        if sys.isWindows():
            ciclop_scan.stop()
            laser_triangulation.cancel()
            platform_extrinsics.cancel()
            self.workbench['control'].videoView.stop()
            self.workbench['calibration'].videoView.stop()
            self.workbench['calibration'].cameraIntrinsicsMainPage.videoView.stop()
            self.workbench['calibration'].laserTriangulationMainPage.videoView.stop()
            self.workbench['calibration'].platformExtrinsicsMainPage.videoView.stop()
            self.workbench['scanning'].videoView.stop()
            driver.board.set_unplug_callback(None)
            driver.camera.set_unplug_callback(None)
            self.workbench['control'].updateStatus(False)
            self.workbench['calibration'].updateStatus(False)
            self.workbench['scanning'].updateStatus(False)
            driver.disconnect()
            # waitCursor = wx.BusyCursor()

        MachineDialog = MachineSettingsDialog(self)
        ret = MachineDialog.ShowModal()

        if ret == wx.ID_OK:
            try:  # TODO: Fix this. If not in the Scanning workbench, _drawMachine() fails.
                self.workbench['scanning'].sceneView._drawMachine()
            except:
                pass
            profile.settings.saveSettings(categories=["machine_settings"])
            self.workbench['scanning'].controls.panels["point_cloud_roi"].updateProfile()

        self.workbench['control'].updateCallbacks()
        self.workbench['adjustment'].updateCallbacks()
        self.workbench['calibration'].updateCallbacks()
        self.workbench['scanning'].updateCallbacks()

    def onMenuViewClicked(self, key, checked, panel):
        profile.settings[key] = checked
        if checked:
            panel.Show()
        else:
            panel.Hide()
        panel.GetParent().Layout()
        panel.Layout()
        self.Layout()

    def onControlPanelClicked(self, event):
        self.onMenuViewClicked('view_control_panel',
                               self.menuControlPanel.IsChecked(),
                               self.workbench['control'].scrollPanel)

    def onControlVideoClicked(self, event):
        self.onMenuViewClicked('view_control_video',
                               self.menuControlVideo.IsChecked(),
                               self.workbench['control'].videoView)

    def onAdjustmentPanelClicked(self, event):
        self.onMenuViewClicked('view_adjustment_panel',
                               self.menuAdjustmentPanel.IsChecked(),
                               self.workbench['adjustment'].scrollPanel)

    def onAdjustmentVideoClicked(self, event):
        self.onMenuViewClicked('view_adjustment_video',
                               self.menuAdjustmentVideo.IsChecked(),
                               self.workbench['adjustment'].videoView)

    def onCalibrationPanelClicked(self, event):
        self.onMenuViewClicked('view_calibration_panel',
                               self.menuCalibrationPanel.IsChecked(),
                               self.workbench['calibration'].scrollPanel)

    def onCalibrationVideoClicked(self, event):
        self.onMenuViewClicked('view_calibration_video',
                               self.menuCalibrationVideo.IsChecked(),
                               self.workbench['calibration'].videoView)

    def onScanningPanelClicked(self, event):
        self.onMenuViewClicked('view_scanning_panel',
                               self.menuScanningPanel.IsChecked(),
                               self.workbench['scanning'].scrollPanel)

    def onScanningVideoSceneClicked(self, event):
        checkedVideo = self.menuScanningVideo.IsChecked()
        checkedScene = self.menuScanningScene.IsChecked()
        profile.settings['view_scanning_video'] = checkedVideo
        profile.settings['view_scanning_scene'] = checkedScene
        self.workbench['scanning'].splitterWindow.Unsplit()
        if checkedVideo:
            self.workbench['scanning'].videoView.Show()
            self.workbench['scanning'].splitterWindow.SplitVertically(
                self.workbench['scanning'].videoView, self.workbench['scanning'].scenePanel)
            if checkedScene:
                self.workbench['scanning'].scenePanel.Show()
            else:
                self.workbench['scanning'].scenePanel.Hide()
                self.workbench['scanning'].splitterWindow.Unsplit()
        else:
            self.workbench['scanning'].videoView.Hide()
            if checkedScene:
                self.workbench['scanning'].scenePanel.Show()
                self.workbench['scanning'].splitterWindow.SplitVertically(
                    self.workbench['scanning'].scenePanel, self.workbench['scanning'].videoView)
                self.workbench['scanning'].splitterWindow.Unsplit()
            else:
                self.workbench['scanning'].scenePanel.Hide()
                self.workbench['scanning'].splitterWindow.Unsplit()

        self.workbench['scanning'].splitterWindow.Layout()
        self.workbench['scanning'].Layout()
        self.Layout()

    def onComboBoxWorkbenchSelected(self, event):
        if _(profile.settings['workbench']) != event.GetEventObject().GetValue():
            profile.settings['workbench'] = self.workbenchDict[event.GetEventObject().GetValue()]
            self.workbenchUpdate()

    def onAbout(self, event):
        info = wx.AboutDialogInfo()
        icon = wx.Icon(resources.getPathForImage("horus.ico"), wx.BITMAP_TYPE_ICO)
        info.SetIcon(icon)
        info.SetName(u'Horus')
        info.SetVersion(version.getVersion())
        techDescription = _('Horus is an Open Source 3D Scanner manager')
        techDescription += '\n' + 'Version: ' + version.getVersion()
        build = version.getBuild()
        if build is not '':
            techDescription += '\n' + 'Build: ' + version.getBuild()
        github = version.getGitHub()
        if github is not '':
            techDescription += '\n' + 'GitHub: ' + version.getGitHub()
        info.SetDescription(techDescription)
        info.SetCopyright(u'(C) 2014-2015 Mundo Reader S.L.')
        info.SetWebSite(u'http://www.bq.com')
        info.SetLicence("""Horus is free software; you can redistribute
it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Horus is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details. You should have
received a copy of the GNU General Public License along with File Hunter;
if not, write to the Free Software Foundation, Inc., 59 Temple Place,
Suite 330, Boston, MA  02111-1307  USA""")
        info.AddDeveloper(u'Jesús Arroyo, Irene Sanz, Jorge Robles')
        info.AddDocWriter(u'Jesús Arroyo, Ángel Larrañaga')
        info.AddArtist(u'Jesús Arroyo, Nestor Toribio')
        info.AddTranslator(
            u'Jesús Arroyo, Irene Sanz, Alexandre Galode, Natasha da Silva, '
            'Camille Montgolfier, Markus Hoedl, Andrea Fantini, Maria Albuquerque, '
            'Meike Schirmeister')

        wx.AboutBox(info)

    def onWelcome(self, event):
        WelcomeWindow(self)

    def onUpdates(self, event):
        if profile.settings['check_for_updates']:
            if version.checkForUpdates():
                VersionWindow(self)
            else:
                dlg = wx.MessageDialog(self, _("You are running the latest version of Horus!"), _(
                    "Updated!"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

    def onBoardUnplugged(self):
        self._onDeviceUnplugged(
            _("Board unplugged"),
            _("Board has been unplugged. Please, plug it in and press connect"))

    def onCameraUnplugged(self):
        self._onDeviceUnplugged(_("Camera unplugged"), _(
            "Camera has been unplugged. Please, plug it in and press connect"))

    def _onDeviceUnplugged(self, title="", description=""):
        ciclop_scan.stop()
        laser_triangulation.cancel()
        platform_extrinsics.cancel()
        self.workbench['control'].updateStatus(False)
        self.workbench['adjustment'].updateStatus(False)
        self.workbench['calibration'].updateStatus(False)
        self.workbench['scanning'].updateStatus(False)
        driver.disconnect()
        dlg = wx.MessageDialog(self, description, title, wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def updateProfileToAllControls(self):
        if profile.settings['view_control_panel']:
            self.workbench['control'].scrollPanel.Show()
            self.menuControlPanel.Check(True)
        else:
            self.workbench['control'].scrollPanel.Hide()
            self.menuControlPanel.Check(False)

        if profile.settings['view_control_video']:
            self.workbench['control'].videoView.Show()
            self.menuControlVideo.Check(True)
        else:
            self.workbench['control'].videoView.Hide()
            self.menuControlVideo.Check(False)

        if profile.settings['view_adjustment_panel']:
            self.workbench['adjustment'].scrollPanel.Show()
            self.menuAdjustmentPanel.Check(True)
        else:
            self.workbench['adjustment'].scrollPanel.Hide()
            self.menuAdjustmentPanel.Check(False)

        if profile.settings['view_adjustment_video']:
            self.workbench['adjustment'].videoView.Show()
            self.menuAdjustmentVideo.Check(True)
        else:
            self.workbench['adjustment'].videoView.Hide()
            self.menuAdjustmentVideo.Check(False)

        if profile.settings['view_calibration_panel']:
            self.workbench['calibration'].scrollPanel.Show()
            self.menuCalibrationPanel.Check(True)
        else:
            self.workbench['calibration'].scrollPanel.Hide()
            self.menuCalibrationPanel.Check(False)

        if profile.settings['view_calibration_video']:
            self.workbench['calibration'].videoView.Show()
            self.menuCalibrationVideo.Check(True)
        else:
            self.workbench['calibration'].videoView.Hide()
            self.menuCalibrationVideo.Check(False)

        if profile.settings['view_scanning_panel']:
            self.workbench['scanning'].scrollPanel.Show()
            self.menuScanningPanel.Check(True)
        else:
            self.workbench['scanning'].scrollPanel.Hide()
            self.menuScanningPanel.Check(False)

        checkedVideo = profile.settings['view_scanning_video']
        checkedScene = profile.settings['view_scanning_scene']

        self.menuScanningVideo.Check(checkedVideo)
        self.menuScanningScene.Check(checkedScene)

        self.workbench['scanning'].splitterWindow.Unsplit()
        if checkedVideo:
            self.workbench['scanning'].videoView.Show()
            self.workbench['scanning'].splitterWindow.SplitVertically(
                self.workbench['scanning'].videoView, self.workbench['scanning'].scenePanel)
            if checkedScene:
                self.workbench['scanning'].scenePanel.Show()
            else:
                self.workbench['scanning'].scenePanel.Hide()
                self.workbench['scanning'].splitterWindow.Unsplit()
        else:
            self.workbench['scanning'].videoView.Hide()
            if checkedScene:
                self.workbench['scanning'].scenePanel.Show()
                self.workbench['scanning'].splitterWindow.SplitVertically(
                    self.workbench['scanning'].scenePanel, self.workbench['scanning'].videoView)
                self.workbench['scanning'].splitterWindow.Unsplit()
            else:
                self.workbench['scanning'].scenePanel.Hide()
                self.workbench['scanning'].splitterWindow.Unsplit()

        self.updateDriverProfile()
        self.updateProfile()

        self.workbenchUpdate()
        self.Layout()

    def updateDriverProfile(self):
        driver.camera.camera_id = int(profile.settings['camera_id'][-1:])
        driver.board.serial_name = profile.settings['serial_name']
        driver.board.baud_rate = profile.settings['baud_rate']
        driver.board.motor_invert(profile.settings['invert_motor'])

    def updateProfile(self):
        ciclop_scan.capture_texture = profile.settings['capture_texture']
        use_laser = profile.settings['use_laser']
        ciclop_scan.set_use_left_laser(use_laser == 'Left' or use_laser == 'Both')
        ciclop_scan.set_use_right_laser(use_laser == 'Right' or use_laser == 'Both')
        ciclop_scan.motor_step = profile.settings['motor_step_scanning']
        ciclop_scan.motor_speed = profile.settings['motor_speed_scanning']
        ciclop_scan.motor_acceleration = profile.settings['motor_acceleration_scanning']
        ciclop_scan.color = struct.unpack(
            'BBB', profile.settings['point_cloud_color'].decode('hex'))

        image_capture.pattern_mode.brightness = profile.settings['brightness_pattern_calibration']
        image_capture.pattern_mode.contrast = profile.settings['contrast_pattern_calibration']
        image_capture.pattern_mode.saturation = profile.settings['saturation_pattern_calibration']
        image_capture.pattern_mode.exposure = profile.settings['exposure_pattern_calibration']
        image_capture.laser_mode.brightness = profile.settings['brightness_laser_scanning']
        image_capture.laser_mode.contrast = profile.settings['contrast_laser_scanning']
        image_capture.laser_mode.saturation = profile.settings['saturation_laser_scanning']
        image_capture.laser_mode.exposure = profile.settings['exposure_laser_scanning']
        image_capture.texture_mode.brightness = profile.settings['brightness_texture_scanning']
        image_capture.texture_mode.contrast = profile.settings['contrast_texture_scanning']
        image_capture.texture_mode.saturation = profile.settings['saturation_texture_scanning']
        image_capture.texture_mode.exposure = profile.settings['exposure_texture_scanning']
        image_capture.use_distortion = profile.settings['use_distortion']

        laser_segmentation.red_channel = profile.settings['red_channel_scanning']
        laser_segmentation.open_enable = profile.settings['open_enable_scanning']
        laser_segmentation.open_value = profile.settings['open_value_scanning']
        laser_segmentation.threshold_enable = profile.settings['threshold_enable_scanning']
        laser_segmentation.threshold_value = profile.settings['threshold_value_scanning']

        current_video.set_roi_view(profile.settings['roi_view'])
        point_cloud_roi.set_diameter(profile.settings['roi_diameter'])
        point_cloud_roi.set_height(profile.settings['roi_height'])

        pattern.rows = profile.settings['pattern_rows']
        pattern.columns = profile.settings['pattern_columns']
        pattern.square_width = profile.settings['pattern_square_width']
        pattern.distance = profile.settings['pattern_origin_distance']

        self.updateCalibrationProfile()

    def updateCalibrationProfile(self):
        resolution = profile.settings['resolution'].split('x')
        driver.camera.set_frame_rate(int(profile.settings['framerate']))
        calibration_data.set_resolution(int(resolution[1]), int(resolution[0]))
        calibration_data.camera_matrix = profile.settings['camera_matrix']
        calibration_data.distortion_vector = profile.settings['distortion_vector']
        calibration_data.laser_planes[0].distance = profile.settings['distance_left']
        calibration_data.laser_planes[0].normal = profile.settings['normal_left']
        calibration_data.laser_planes[1].distance = profile.settings['distance_right']
        calibration_data.laser_planes[1].normal = profile.settings['normal_right']
        calibration_data.platform_rotation = profile.settings['rotation_matrix']
        calibration_data.platform_translation = profile.settings['translation_vector']

    def updateDriver(self):
        resolution = profile.settings['resolution'].split('x')
        driver.camera.set_resolution(int(resolution[0]), int(resolution[1]))

    def workbenchUpdate(self, layout=True):
        currentWorkbench = profile.settings['workbench']

        wb = {'Control workbench': self.workbench['control'],
              'Adjustment workbench': self.workbench['adjustment'],
              'Calibration workbench': self.workbench['calibration'],
              'Scanning workbench': self.workbench['scanning']}

        waitCursor = wx.BusyCursor()

        self.updateDriver()

        self.menuFile.Enable(self.menuLoadModel.GetId(), currentWorkbench == 'Scanning workbench')
        self.menuFile.Enable(self.menuSaveModel.GetId(), currentWorkbench == 'Scanning workbench')
        self.menuFile.Enable(self.menuClearModel.GetId(), currentWorkbench == 'Scanning workbench')

        wb[currentWorkbench].updateProfileToAllControls()
        wb[currentWorkbench].combo.SetValue(_(currentWorkbench))

        if layout:
            for key in wb:
                if wb[key] is not None:
                    if key == currentWorkbench:
                        wb[key].Hide()
                        wb[key].Show()
                    else:
                        wb[key].Hide()

            self.Layout()

        del waitCursor

        gc.collect()
