#!/usr/bin/env python3

# System modules
import json
import os
import time
import typing

# Third party modules
import zmq
from DBP import Protocols


class Message():
    """
    A class to handel all broker related messaging including asserting formats, sending, and receiving.
    Requires a socket to pull messages off of and is capable of handeling JSON, buffers(arrays), strings
    , pickles, and custom serializations.

    Attributes
    ----------
    socket : zmq.Socket
        a socket from which to pull messages off of and send through
    message : zmq.Frame
        a multi frame message object which holds the raw incoming message
    outgoing : list[str]
        The outgoing multi part message with the first frame containing the address or the requestor
        and a blank delimiter frame.
    valid : bool
        Used to determine if the incoming message adheres to the formating protocol
    protocol : str
        defines the type of incoming message to check. Currently there are two protocols a valid
        message can be:
            + DBP Core Catalog/Service v0.1 (DBPCCS01)
            + DBP Core Catalog/Client v0.1 (DBPCCC01)
    protocol : Protocols
        Tell the message which DBP protocol to use
    """

    def __init__(self, protocol=None, socket: zmq.Socket = None):
        self.valid = True
        self.socket = socket

        self.body = None
        self.incoming = None
        self.command = None
        self.return_addr = None
        self.protocol = protocol
        self.outgoing = []

    def recv(self):
        """
        Receives the first multipart message on behalf of the polled socket, formats the outgoing
        attribute's message header, and caches the payload.

        Parameters
        ----------
        """
        self.incoming = self.socket.recv_multipart()
        self.incoming_raw = self.incoming.copy()
        self.validate_envelope()

    def send(self, command='', body='', display=False):
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

        # ZMQ requires messages be sent as bytes which is fine for strings in python2, but
        # for string in python3, they must first be converted with the bytes function.

        # Outgoing message header formating. ORDER MATTERS
        if self.socket.socket_type == zmq.ROUTER:
            self.add_frame(self.return_addr)
            self.add_frame('')

        self.add_frame(self.protocol)
        self.add_frame(command)
        self.add_frame(body)

        if display:
            self.display_envelope(incoming=False)

        self.socket.send_multipart(self.outgoing)

    def add_frame(self, body):
        """
        Converts objects to zmq frame(s) and appends it/them to the multipart outgoing message attribute.

        Parameters
        ----------
        body : Any
            This is the message to append to the outgoing message attribute.
        """

        # TODO: add support for pickle, ect type containers
        if type(body) == bytes:
            self.outgoing.append(body)

        elif type(body) == str:
            self.outgoing.append(bytes(body, 'utf-8'))

        elif type(body) == dict:
            self.outgoing.append(bytes(json.dumps(body), 'utf-8'))

    def validate_envelope(self):
        """
        validates incoming message using the Distributed Broker Protocol
        Core Catalog sub-protobols defined in the README.md and pops and caches elements.
        """
        # General message check
        if self.socket.socket_type == zmq.ROUTER:
            # Caches the return address of the requestor
            self.return_addr = self.incoming.pop(0)

            # Checks for blank delimiter
            delimiter = self.incoming.pop(0)
            if delimiter != b'':
                self.valid = False

        # Verifies if proper protocol
        self.protocol = self.incoming.pop(0)
        if (self.protocol in Protocols):
            if self.protocol == Protocols[0]:
                # Assigns whatever is left to the body
                self.body = self.incoming
            else:  # if Protocols.Service
                # pulls off the command byte then assigns whatever is left to body
                # TODO: Check if sent command is a valid operation
                self.command = self.incoming.pop(0)
                self.body = self.incoming
        else:
            self.valid = False

        if not self.valid:
            self.send("Error: Invalid Message Envelope.")

    def display_envelope(self, incoming=True, raw=True):
        """
        Prints out all parts of either the current outgoing or incoming message

        Parameters
        ----------
        incoming : bool, default=True
            Flag to determine which message to see. True for incoming false for outgoing
        raw : bool, default=True
            Flag to determine if to disply original message before validation.
        """
        print(
            f"{'Incoming' if incoming else 'Outgoing '} Message {'Body ' if not raw else ''}Envelope:")

        if incoming:
            if raw:
                message = self.incoming_raw
            else:
                message = self.incoming

        else:
            message = self.outgoing

        for index, frame in enumerate(message):
            print(f"\tFrame {index}: {frame}")
