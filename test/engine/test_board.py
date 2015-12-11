import unittest
from horus.engine.driver.board import Board


class BoardTest(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_serial_name(self):
        self.assertEqual(self.board.serial_name, '/dev/ttyUSB0')

    def test_baud_rate(self):
        self.assertEqual(self.board.baud_rate, 115200)
