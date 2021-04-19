
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

    def test_publish(self):
        self.assertEquals(1, 1)
