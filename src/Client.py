#!/usr/bin/env python3

# System modules
import os
import time
import logging
from typing import get_args

# Third party modules
import zmq

# Relative imports
from Node import Node
from Message import Message
from Beacon import Beacon
from DBP import commands


class Client(Node):
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
        msg = Message(socket=self.sockets["client->bus"])
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
        # self.get_services()
        addr = input("Specify connection port:  ")
        self.connect_to_service(f'tcp://localhost:{addr}')
        msg = input("What would you like to say: ")

        message = Message(
            command=commands['Info_Req'],
            socket=self.sockets["client->service"],
            logger=self.logger)
        message.send(body=msg)

        print("Response from service:")
        message.recv(display=True)


if __name__ == "__main__":
    print("Shalom, World!")

    ctx = zmq.Context()
    addr = input("Specify connection port:  ")
    req = ctx.socket(zmq.REQ)
    req.connect(f'tcp://localhost:{addr}')
    msg = input("What would you like to say: ")

    message = Message(socket=req)
    message.send(command='u_U', body=msg, display=True)

    print("Response from service:")
    message.recv(display=True)
