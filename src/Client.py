#!/usr/bin/env python3

# System modules
import os
import time
import logging
from typing import get_args

# Third party modules
import zmq

# Relative imports
from BaseClasses import BaseNode
from Message import Message
from Beacon import Beacon


class Client(BaseNode):
    """
    A LIAMb node extension to provide a client interface with the bus.
    """

    def __init__(self, name="Gondor"):
        super().__init__(name=name, log_level=logging.DEBUG)

        # open a socket to the broker
        self.new_socket("client->bus", zmq.REQ)

    def get_services(self, name=None):
        """
        Get a list or entry of registered service(s) information.

        Parameter
        ---------
        name : str, default=None
            A name of a desired service to get information about. If left blank then all services 
            will be returned
        """
        msg = Message(protocol='DBPCCC01', socket=self.sockets["client->bus"])
        msg.send(name)
        msg.recv()
        msg.display_envelope()

    def connect_to_service(self, addr):
        """
        Connects the client to a service at the specified address. One can either be provide or found
        by asking the bus broker node.

        Parameters
        ----------
        addr: str
            An address to connect the client to.
        """
        self.new_socket("client->service", zmq.REQ, addr)

    def start(self):
        """
        An event loop for user interaction with the client API.
        """
        service = input("Please enter a service to chat with: ")
        self.get_services(name=service)
        addr = input("Specify connection address:  ")
        self.connect_to_service(addr)
        msg = input("What would you like to say: ")

        message = Message(protocol="DBPCCC01",
                          socket=self.sockets["client->service"])
        message.send(body=msg)

        print("Response from service:")
        message.recv()
        message.display_envelope()


if __name__ == "__main__":
    print("Shalom, World!")

    test = Client()
    test.start()
