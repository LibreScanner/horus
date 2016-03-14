# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import wx._core
import logging.config
import datetime

from horus.gui.main import MainWindow
from horus.gui.splash import SplashScreen
from horus.gui.welcome import WelcomeDialog

from horus.util import profile, resources, version, system as sys
from horus.gui.util.version_window import VersionWindow


class HorusApp(wx.App):

    def __init__(self):
        super(HorusApp, self).__init__(redirect=False)

        self.splash = None

        if sys.is_darwin():
            self.after_splash_callback()
        else:
            self.splash = SplashScreen(self.after_splash_callback)

    def after_splash_callback(self):
        # Load settings
        profile.load_settings()

        # Load logger
        self.clear_log_if_required()
        logging.config.fileConfig(resources.get_path_for_logger('logger.conf'))

        # Load language
        resources.setup_localization(profile.settings['language'])

        # Load version
        version.download_lastest_data()

        # Create main window
        self.main_window = MainWindow()

        # Check for updates
        if profile.settings['check_for_updates'] and version.check_for_updates():
            v = VersionWindow(self.main_window)
            if v.download:
                if self.splash is not None:
                    self.splash.Show(False)
                    self.splash = None
                self.main_window.Close(True)
                return

        # Hide Splash
        if self.splash is not None:
            self.splash.Show(False)
            self.splash = None

        # Show main window
        self.SetTopWindow(self.main_window)
        self.main_window.Show()

        if profile.settings['show_welcome']:
            # Create welcome window
            WelcomeDialog(self.main_window)

        set_full_screen_capable(self.main_window)

        if sys.is_darwin():
            wx.CallAfter(self.stupid_mac_os_workaround)

    def __del__(self):
        # Save profile and preferences
        profile.settings.save_settings()

    def clear_log_if_required(self):
        date_format = '%Y-%m-%d %H:%M:%S'
        current_log_date = datetime.datetime.now()
        last_log_date = profile.settings['last_clear_log_date']
        try:
            last_log_date = datetime.datetime.strptime(last_log_date, date_format)
            # Remove log if have elapsed 7 days after last log clear
            if (current_log_date - last_log_date).days >= 7:
                with open('horus.log', 'w'):
                    pass
        except:
            pass
        self._update_log_date()

    def _update_log_date(self):
        date_format = '%Y-%m-%d %H:%M:%S'
        current_log_date = datetime.datetime.now()
        profile.settings['last_clear_log_date'] = str(current_log_date.strftime(date_format))

    def MacReopenApp(self):
        self.GetTopWindow().Raise()

    def stupid_mac_os_workaround(self):
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

        def set_full_screen_capable(frame):
            frameobj = _objc.PyObjCObject_New(frame.GetHandle(), 0, 1)

            NSWindowCollectionBehaviorFullScreenPrimary = 1 << 7
            window = frameobj.window()
            newBehavior = window.collectionBehavior() | NSWindowCollectionBehaviorFullScreenPrimary
            window.setCollectionBehavior_(newBehavior)
    except:
        def set_full_screen_capable(frame):
            pass

else:
    def set_full_screen_capable(frame):
        pass
