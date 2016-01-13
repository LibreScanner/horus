# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import threading

from horus import Singleton
from horus.engine.driver.board import Board
from horus.engine.driver.camera import Camera


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
        self.__init__()
        if self._before_callback is not None:
            self._before_callback()
        threading.Thread(target=self._connect).start()

    def _connect(self):
        exception = None
        self.is_connected = False
        try:
            self.camera.connect()
            self.board.connect()
        except Exception as e:
            exception = e
        else:
            self.is_connected = True
        finally:
            if exception is None:
                self.unplugged = False
                response = (True, self.is_connected)
            else:
                response = (False, exception)
                self.disconnect()
            if self._after_callback is not None:
                self._after_callback(response)

    def disconnect(self):
        self.is_connected = False
        self.camera.disconnect()
        self.board.disconnect()

    def set_callbacks(self, before, after):
        self._before_callback = before
        self._after_callback = after
