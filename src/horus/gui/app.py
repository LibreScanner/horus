# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core

from horus.gui.main import MainWindow
from horus.gui.splash import SplashScreen
from horus.gui.welcome import WelcomeWindow

from horus.util import profile, resources, version, system as sys
from horus.gui.util.versionWindow import VersionWindow


class HorusApp(wx.App):

    def __init__(self):
        super(HorusApp, self).__init__(redirect=False)

        if sys.is_darwin():
            self.after_splash_callback()
        else:
            SplashScreen(self.after_splash_callback)

    def after_splash_callback(self):
        # Load Settings
        profile.load_settings()

        # Load Language
        resources.setup_localization(profile.settings['language'])

        # Create Main Window
        self.main_window = MainWindow()

        # Check for updates
        if profile.settings['check_for_updates'] and version.check_for_updates():
            v = VersionWindow(self.main_window)
            if v.download:
                return

        # Show Main Window
        self.SetTopWindow(self.main_window)
        self.main_window.Show()

        if profile.settings['show_welcome']:
            # Create Welcome Window
            WelcomeWindow(self.main_window)

        setFullScreenCapable(self.main_window)

        if sys.is_darwin():
            wx.CallAfter(self.StupidMacOSWorkaround)

    def __del__(self):
        # Save Profile and Preferences
        profile.settings.save_settings()

    def MacReopenApp(self):
        self.GetTopWindow().Raise()

    def StupidMacOSWorkaround(self):
        """
        On MacOS for some magical reason opening new frames does not work
        until you opened a new modal dialog and closed it. If we do this from
        software, then, as if by magic, the bug which prevents opening extra frames is gone.
        """
        dlg = wx.Dialog(None, size=(1, 1))
        wx.PostEvent(dlg, wx.CommandEvent(wx.EVT_CLOSE.typeId))
        dlg.ShowModal()
        dlg.Destroy()

if sys.is_darwin():  # Mac magic. Dragons live here. This sets full screen options.
    try:
        import ctypes
        import objc
        _objc = ctypes.PyDLL(objc._objc.__file__)

        # PyObject *PyObjCObject_New(id objc_object, int flags, int retain)
        _objc.PyObjCObject_New.restype = ctypes.py_object
        _objc.PyObjCObject_New.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

        def setFullScreenCapable(frame):
            frameobj = _objc.PyObjCObject_New(frame.GetHandle(), 0, 1)

            NSWindowCollectionBehaviorFullScreenPrimary = 1 << 7
            window = frameobj.window()
            newBehavior = window.collectionBehavior() | NSWindowCollectionBehaviorFullScreenPrimary
            window.setCollectionBehavior_(newBehavior)
    except:
        def setFullScreenCapable(frame):
            pass

else:
    def setFullScreenCapable(frame):
        pass
