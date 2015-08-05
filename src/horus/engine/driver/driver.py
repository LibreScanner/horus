# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import threading

from board import Board, WrongFirmware, BoardNotConnected
from camera import Camera, CameraNotConnected, WrongCamera, InvalidVideo

import horus.util.error as Error
from horus.util.singleton import Singleton


@Singleton
class Driver(object):

    """Driver class. For managing scanner hw"""

    def __init__(self):
        self.board = Board(self)
        self.camera = Camera(self)
        self.is_connected = False
        self.unplugged = False

        # TODO: Callbacks to Observer pattern
        self._before_callback = None
        self._after_callback = None

    def connect(self):
        if self._before_callback is not None:
            self._before_callback()
        threading.Thread(target=self._connect, args=(self._after_callback,)).start()

    def _connect(self, callback):
        error = None
        self.is_connected = False
        try:
            self.camera.connect()
            self.board.connect()
        except WrongFirmware:
            error = Error.WrongFirmware
        except BoardNotConnected:
            error = Error.BoardNotConnected
        except CameraNotConnected:
            error = Error.CameraNotConnected
        except WrongCamera:
            error = Error.WrongCamera
        except InvalidVideo:
            error = Error.InvalidVideo
        else:
            self.is_connected = True
        finally:
            if error is None:
                self.unplugged = False
                response = (True, self.is_connected)
            else:
                response = (False, error)
                self.disconnect()
            if callback is not None:
                callback(response)

    def disconnect(self):
        self.is_connected = False
        self.camera.disconnect()
        self.board.disconnect()

    def set_callbacks(self, before, after):
        self._before_callback = before
        self._after_callback = after

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Driver, cls).__new__(cls, *args, **kwargs)
        return cls._instance
