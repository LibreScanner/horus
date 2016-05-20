# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

__version__ = '0.2rc1'
__datetime__ = ''
__commit__ = ''


def Singleton(class_):
    class class_w(class_):
        _instance = None

        def __new__(class_, *args, **kwargs):
            if class_w._instance is None:
                class_w._instance = super(class_w, class_).__new__(class_, *args, **kwargs)
                class_w._instance.__initialized = False
            return class_w._instance

        def __init__(class_, *args, **kwargs):
            if class_w._instance.__initialized:
                return
            super(class_w, class_).__init__(*args, **kwargs)
            class_w._instance.__initialized = True

    class_w.__name__ = class_.__name__
    return class_w
