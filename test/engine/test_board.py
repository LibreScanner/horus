# coding=utf-8

__author__ = "Jesús Arroyo Torrens <jesus.arroyo@bq.com>"
__license__ = "GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html"
__copyright__ = "Copyright (C) 2015 Mundo Reader S.L. - Released under terms of the GPLv2 License"


import unittest

from horus.engine.board import Board

class BoardTest(unittest.TestCase):

	def setUp(self):
		self.board = Board()

	def test_serial_name(self):
		self.assertEqual(self.board.serialName, '/dev/ttyUSB0')

	def test_baud_rate(self):
		self.assertEqual(self.board.baudRate, 115200)