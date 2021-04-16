#!/usr/bin/env python3

# System modules
import json
import time
import struct
import logging
from typing import Dict, List, Any

# Third party modules
import zmq
from Hermes.DBP import command_checks, commands
from Hermes.zhelpers import dump

# NOTE: This is an example of including zeromq sockets within the wrapper as opposed to how Heartbeats deal with events.
# Refer to the Clone patter KVMsg for reference


class Message():
    """
    A class to handel all broker related messaging including asserting formats, sending, and receiving.
    Requires a socket to pull messages off of and is capable of handeling JSON, buffers(arrays), strings
    , pickles, and custom serializations.

    Attributes
    ----------
    socket : zmq.Socket
        a socket from which to pull messages off of and send through
    Incomeing : zmq.Frame
        a multi frame message object which holds the raw incoming message
    outgoing : List[str]
        The outgoing multi part message with the first frame containing the address or the requestor
        and a blank delimiter frame.
    valid : bool
        Used to determine if the incoming message adheres to the formating protocol
    """

    def __init__(self, socket: zmq.Socket, logger=None):
        self.valid: bool = True
        self.socket: zmq.Socket = socket

        self.body: Any = None
        self.incoming: List[bytes] = None
        self.command: bytes = None
        self.return_addr: bytes = None
        self.outgoing: List[bytes] = []
        self.time: float = None

        if logger is not None:
            self.logger: logging.Logger = logger
        else:
            self.logger: logging.Logger = logging.getLogger(__name__)

    def recv(self, display=False):
        """
        Receives the first multipart message on behalf of the polled socket, formats the outgoing
        attribute's message header, and caches the payload.

        Parameters
        ----------
        """
        self.incoming = self.socket.recv_multipart()
        self.incoming_raw = self.incoming.copy()  # For debugging

        # Req, Rep, and Dealer sockets already do this part. Routers must do it manually
        if self.socket.socket_type == zmq.ROUTER:
            # Caches the return address of the requestor
            self.return_addr = self.incoming.pop(0)

            # Checks for blank delimiter
            delimiter = self.incoming.pop(0)
            if delimiter != b'':
                self.valid = False

        if len(self.incoming) >= 3:
            # Command validity is left up to the service.
            self.command = self.incoming.pop(0)
            self.time = struct.unpack('f', self.incoming.pop(0))[0]
            self.body = self.incoming

        else:
            self.valid = False

        if not self.valid:
            self.logger.info("Incoming message invalid. Disregarding...")
            self.send(invalid=True)

        if display:
            self.display_envelope(raw=True, message=self.incoming_raw)

    def send(self, command='', body='', display=False, invalid=False):
        """
        Sends the current multipart outgoing message attribute on behalf of the polled
        socket.

        Parameters
        ----------
        command: str
            The command with which to send the message with.
        body: Any
            The payload for which the message will hold.
        display : bool
            A flag for displaying outgoing message frames to the console as it sends
        """

        # Outgoing message header formating. ORDER MATTERS
        if self.socket.socket_type == zmq.ROUTER:
            self.add_frame(self.return_addr)
            self.add_frame('')

        self.add_frame(command)
        self.add_frame(time.time())

        if invalid:
            self.add_frame("Error: Invalid Message Envelope.")
        else:
            self.add_frame(body)

        if display:
            self.display_envelope(raw=True, message=self.outgoing)

        self.logger.debug("Putting message on outgoing queue.")
        self.socket.send_multipart(self.outgoing)

    def add_frame(self, body):
        """
        Converts objects to zmq frame(s) and appends it/them to the multipart outgoing message attribute.

        Parameters
        ----------
        body : Any
            This is the message to append to the outgoing message attribute.
        """
        # TODO: Allow for positional placement parameters
        # TODO: Implement with msgpack.
        # TODO: Standardize body as json

        if type(body) == bytes:
            self.outgoing.append(body)

        elif type(body) == str:
            self.outgoing.append(bytes(body, 'utf-8'))

        elif type(body) == dict:
            self.outgoing.append(bytes(json.dumps(body), 'utf-8'))

        elif type(body) == float:
            self.outgoing.append(struct.pack('f', body))

        elif type(body) == int:
            self.outgoing.append(struct.pack('i', body))

    def display_envelope(self, raw=True, message: List[bytes] = None):
        """
        Prints out all parts of either the current outgoing or incoming message

        Parameters
        ----------
        incoming : bool, default=True
            Flag to determine which message to see. True for incoming false for outgoing
        raw : bool, default=True
            Flag to determine if to disply original message before validation.
        """
        if raw and message is not None:
            for index, frame in enumerate(message):
                print(f"\tFrame {index}: {frame}")

        else:
            print(
                f"Message Frames: \n\tReturn Address:\t{self.return_addr}\n\tTime Sent:\t{self.time}\n\tCommand:\t{self.command}\n\tBody:\t\t{self.body}")
