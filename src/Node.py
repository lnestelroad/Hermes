#!/usr/bin/env python3

# System modules
import json
import os
import time
import logging
import typing
from uuid import uuid4

# Third party modules
import zmq
from Beacon import Beacon
from Logger import Logger


class Node():
    """
    Base class to set up a basic zmq instance (also referred to as a node) for later inheritance.

    Attributes
    ----------
    name : str
        An identification for the inherited node. Used for the logger
    ctx : zmq.Context
        Holds the Nodes context
    sockets : dict{name: zmq.Socket}
        A dictionary containing all of the sockets exposed on the node with an
        initialized pair socket object to be replaced by a specified type
    ip : str, default="localhost"
        An IP address for which the node with either bind or connect to.
    port : str, default="5246"
        A starting value for the ports on which sockets will be attached to.
    addr : str
        A formated string of the socket for which the node will bind/connect to.
    update : bool, default=False
        A flag to signify that the node needs to send a message to the broke with the new
        values.
    """

    def __init__(self, name=uuid4().hex, ip="127.0.0.1", port=5246, log_level=logging.WARNING):
        self.name = name
        self.port = port
        self.ip = ip
        self.addr = f"tcp://{ip}:{port}"
        self.update = False

        self.ctx = zmq.Context()
        self.poller = zmq.Poller()
        self.sockets = dict()

        # Initialize logging component
        self.logger = Logger(name, log_level).logger

    def new_socket(self, name, type, addr=None, soc_options=None):
        """
        A socket factory. Generates new socket types, attaches them to current port number+1, and
        appends it to the sockets list.

        Parameters
        ----------
        name : str
            A name to give the new socket
        type : zmq.Socket, default=zmq.PAIR
            A zmq socket type for the new socket
        soc_options : dict()
            passes along all of the wanted socket options including... TODO: ADD SOCKET OPTIONS
        addr : str, default=None
            A remote addres to connect to for REQ, DEALER, or SUB socket types. Will attempt to 
            connect to tcp://localhost:5246 if nothing else is provided.
        """
        # TODO: ITERATE THROUGH SOCKET OPTIONS PARAMETER

        self.sockets[name] = self.ctx.socket(type)

        if (type == zmq.REQ or type == zmq.DEALER or type == zmq.SUB):
            if addr is not None:
                self.sockets[name].connect(addr)
                self.logger.info(
                    f"Connecting Socket to Remote Address: {addr}")
            else:
                self.sockets[name].connect(self.addr)
                self.logger.info(
                    f"Connecting Socket to Local Address: {self.addr}")

        elif(type == zmq.REP or type == zmq.ROUTER or type == zmq.PUB):

            # If there is a port conflict, increment by one and try again:

            while True:
                try:
                    self.sockets[name].bind(f"tcp://*:{self.port}")
                    self.logger.info(
                        f"Opened New Socket: '{name}' on Port {self.port}")

                    # If the port binding failed, then don't update the port value as it was already
                    # done in the except. This simply stops double increments
                    if not self.update:
                        self.port += 1
                    break

                except zmq.ZMQError as e:
                    self.port += 1
                    self.logger.warning(
                        f"Port Conflict. Attemping to Bind With New Port: {self.port}")
                    self.logger.debug(f"Error Code: {e}")
                    self.update = True

        self.poller.register(self.sockets[name], flags=zmq.POLLIN)

    def new_pipe(self, pipe: zmq.Socket):
        """
        Registers a new pipe socket with the node.

        Parameters
        ----------
        pipe: zmq.Socket
            A PAIR sockets to be passed in from a parent thread.
        """
        self.sockets['pipe'] = pipe
        self.poller.register(self.sockets['pipe'], flags=zmq.POLLIN)

    def close_socket(self, name: str):
        """
        Closes a socket and removes it from the sockets list.

        Parameters
        ----------
        name : str
            The name of the socket to close.
        """
        self.sockets[name].close()
        del self.sockets[name]

        self.logger.info(f"Removed Socket: {name}")

    def close_ctx(self):
        """
        Closes all of the sockets instances then destroys the context.
        """
        self.ctx.destroy()
        self.logger.info("Sockets Closed and Context Destroyed.")
