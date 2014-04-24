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

__author__ = u"Álvaro Velad Galván <alvaro.velad@bq.com>"
__license__ = u"GNU General Public License v3 http://www.gnu.org/licenses/gpl.html"

import os
from horus.language import es_es
from horus.language import en_us

EN_US = u"en_us"
ES_ES = u"es_es"

f = open(os.path.join(os.path.dirname(__file__), "../resources/language.txt"))
locale = f.read()
f.close()

# Por defecto todas las string estan en ingles. Si el idioma por defecto es otro y no se encuentra la string, se busca en ingles.
def getString(string):
	if locale == EN_US:
		return getattr(en_us, string)
	elif locale == ES_ES:
		try:
			return getattr(es_es, string)
		except AttributeError:
			return getattr(en_us, string)
