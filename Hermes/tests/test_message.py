
# Standard imports
import unittest

# Relative import
import Hermes.Message

# External imports
import zmq


class TestMessage(unittest.TestCase):

    def setUp(self) -> None:
        """
        Brings up a zmq context and socket for the message tests to simulate with.
        """
        self.ctx = zmq.Context()
        self.soc = self.ctx.socket(zmq.REQ)

    def test_format(self):
        self.assertEqual(1, 1)

    def test_recv(self):
        self.assertEqual(1, 1)

    def test_send(self):
        self.assertEqual(1, 2)

    def test_add_frame(self):
        self.assertEqual(1, 1)

    def test_display(self):
        self.assertEqual(1, 1)
